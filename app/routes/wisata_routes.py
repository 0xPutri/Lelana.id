from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, limiter
from app.models.wisata import Wisata
from app.models.review import Review
from app.models.foto_ulasan import FotoUlasan
from app.forms import WisataForm, ReviewForm
from app.utils.decorators import admin_required
from app.services.file_handler import save_pictures
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import FlaskForm
from app.utils.text_filters import censor_text

# Membuat Blueprint untuk rute-rute terkait wisata
wisata = Blueprint('wisata', __name__)

@wisata.route('/wisata')
def list_wisata():
    """Menampilkan daftar semua tempat wisata dengan sistem pagination.

    Returns:
        Response: Render template halaman daftar wisata dengan data wisata
                  dan kontrol pagination.
    """
    # Mengambil nomor halaman dari query parameter URL, default ke halaman 1
    page = request.args.get('page', 1, type=int)

    # Melakukan query ke database dengan pagination
    pagination = Wisata.query.order_by(Wisata.nama).paginate(
        page=page, per_page=5, error_out=False
    )
    # Mendapatkan item wisata untuk halaman saat ini
    daftar_wisata_halaman_ini = pagination.items

    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('wisata/list.html', 
                            daftar_wisata=daftar_wisata_halaman_ini, 
                            pagination=pagination, 
                            delete_form=delete_form)

@wisata.route('/wisata/detail/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per hour", methods=["POST"], key_func=lambda: current_user.id)
def detail_wisata(id):
    """Menampilkan detail tempat wisata dan menangani pengiriman ulasan.

    Untuk metode GET, menampilkan detail wisata dan daftar ulasan.
    Untuk metode POST, memproses pengiriman ulasan baru dari pengguna.

    Args:
        id (int): ID dari tempat wisata yang akan ditampilkan.

    Returns:
        Response: Render template halaman detail wisata.
    """
    # Mengambil data wisata dari database, atau 404 jika tidak ada
    w = db.session.get(Wisata, id)
    if w is None:
        abort(404)
    form = ReviewForm()

    # Blok ini dieksekusi hanya jika ada pengiriman form (POST) yang valid
    if form.validate_on_submit() and current_user.is_authenticated:
        # Membuat objek ulasan baru
        review_baru = Review(
            rating=form.rating.data,
            komentar=censor_text(form.komentar.data),
            author=current_user,
            wisata_reviewed=w
        )
        db.session.add(review_baru)

        # Memeriksa apakah ada file foto yang diunggah
        if form.foto.data and form.foto.data[0].filename:
            try:
                # Menyimpan gambar menggunakan file handler dan mendapatkan nama filenya
                filenames = save_pictures(form.foto.data)
                # Membuat objek FotoUlasan untuk setiap file yang disimpan
                for filename in filenames:
                    foto_baru = FotoUlasan(nama_file=filename, review=review_baru)
                    db.session.add(foto_baru)
            except ValueError as e:
                # Rollback jika terjadi error validasi file (misal: bukan gambar)
                db.session.rollback()
                current_app.logger.warning('User %s gagal unggah foto ulasan: %s', 
                    current_user.username, str(e), exc_info=True
                )
                flash(f'Gagal mengunggah: {e}', 'danger')
                return redirect(url_for('wisata.detail_wisata', id=w.id))
            except SQLAlchemyError as e:
                # Rollback jika terjadi error saat menyimpan ke database
                db.session.rollback()
                current_app.logger.error('Database error saat menyimpan foto ulasan untuk user %s: %s', 
                    current_user.username, str(e), exc_info=True
                )
                flash('Terjadi kesalahan pada database. Silakan coba lagi.', 'danger')
                return redirect(url_for('wisata.detail_wisata', id=w.id))
            except Exception as e:
                # Rollback untuk error tak terduga lainnya
                db.session.rollback()
                current_app.logger.critical('Error tidak terduga saat user %s mengunggah foto: %s', 
                    current_user.username, str(e), exc_info=True
                )
                flash('Terjadi kesalahan internal yang tidak terduga. Tim kami telah diberitahu.', 'danger')
                return redirect(url_for('wisata.detail_wisata', id=w.id))

        # Menyimpan semua perubahan (review dan foto) ke database
        db.session.commit()
        flash('Terima kasih! Review Anda telah ditambahkan.', 'success')
        return redirect(url_for('wisata.detail_wisata', id=w.id))
    
    # Query untuk mengambil semua review terkait wisata ini (untuk metode GET)
    # Menggunakan eager loading untuk efisiensi
    semua_review = w.reviews.options(
        joinedload(Review.author),
        subqueryload(Review.foto)
    ).order_by(Review.tanggal_dibuat.desc()).all()

    return render_template('wisata/detail.html', wisata=w, reviews=semua_review, form=form)

@wisata.route('/wisata/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def tambah_wisata():
    """Menangani pembuatan data tempat wisata baru oleh admin.

    Returns:
        Response: Render template form, atau redirect ke daftar wisata
                  setelah berhasil dibuat.
    """
    form = WisataForm()
    if form.validate_on_submit():
        # Membuat instance Wisata baru dari data form
        wisata_baru = Wisata(
            nama=form.nama.data,
            kategori=form.kategori.data,
            lokasi=form.lokasi.data,
            deskripsi=form.deskripsi.data,
            gambar_url=form.gambar_url.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        db.session.add(wisata_baru)
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menambahkan Wisata baru "%s" (ID: %d).', 
            current_user.username, wisata_baru.nama, wisata_baru.id
        )

        flash('Destinasi wisata baru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.manage_wisata'))
    
    return render_template('wisata/tambah_edit.html', form=form, judul_halaman='Tambah Wisata')

@wisata.route('/wisata/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def edit_wisata(id):
    """Menangani pembaruan data tempat wisata yang sudah ada oleh admin.

    Args:
        id (int): ID dari tempat wisata yang akan diedit.

    Returns:
        Response: Render template form, atau redirect ke detail wisata
                  setelah berhasil diperbarui.
    """
    # Mengambil data wisata dari database, atau 404 jika tidak ada
    wisata_item = db.session.get(Wisata, id)
    if wisata_item is None:
        abort(404)
    # Menginisialisasi form dengan data dari objek wisata
    form = WisataForm(obj=wisata_item)

    if form.validate_on_submit():
        # Memperbarui atribut objek dengan data dari form
        wisata_item.nama = form.nama.data
        wisata_item.kategori = form.kategori.data
        wisata_item.lokasi = form.lokasi.data
        wisata_item.deskripsi = form.deskripsi.data
        wisata_item.gambar_url = form.gambar_url.data
        wisata_item.latitude = form.latitude.data
        wisata_item.longitude = form.longitude.data
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s memperbarui Wisata "%s" (ID: %d).', 
            current_user.username, wisata_item.nama, wisata_item.id
        )

        flash('Data wisata berhasil diperbarui!', 'success')
        return redirect(url_for('admin.manage_wisata'))
    
    return render_template('wisata/tambah_edit.html', form=form, judul_halaman='Edit Wisata')

@wisata.route('/wisata/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_wisata(id):
    """Memproses permintaan penghapusan tempat wisata.

    Memerlukan validasi token CSRF sebelum menghapus data.

    Args:
        id (int): ID dari tempat wisata yang akan dihapus.

    Returns:
        Response: Redirect ke halaman daftar wisata dengan pesan status.
    """
    # Mengambil data wisata dari database, atau 404 jika tidak ada
    wisata_item = db.session.get(Wisata, id)
    if wisata_item is None: abort(404)
    
    # Membuat instance form kosong untuk validasi CSRF
    form = FlaskForm()
    if form.validate_on_submit():
        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menghapus Wisata "%s" (ID: %d).', 
            current_user.username, wisata_item.nama, wisata_item.id
        )
        
        # Menghapus objek dari database
        db.session.delete(wisata_item)
        db.session.commit()
        flash('Data wisata telah berhasil dihapus.', 'info')
    else:
        # Gagal jika token CSRF tidak valid
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('admin.manage_wisata'))

@wisata.route('/api/wisata/lokasi')
@limiter.limit("60 per minute")
def api_lokasi_wisata():
    """Menyediakan endpoint API untuk data lokasi geografis semua wisata.

    Mengembalikan daftar tempat wisata yang memiliki data latitude dan longitude
    dalam format JSON, cocok untuk digunakan oleh pustaka peta (e.g., Leaflet).

    Returns:
        Response: Objek JSON berisi daftar lokasi wisata.
    """
    # Query untuk mengambil hanya data yang memiliki koordinat
    query_result = db.session.query(
        Wisata.id,
        Wisata.nama,
        Wisata.latitude,
        Wisata.longitude
    ).filter(Wisata.latitude.isnot(None), Wisata.longitude.isnot(None)).all()

    # Mengubah hasil query menjadi format list of dictionaries
    daftar_lokasi = [
        {
            'nama': nama,
            'lat': lat,
            'lon': lon,
            'detail_url': url_for('wisata.detail_wisata', id=id, _external=True)
        }
        for id, nama, lat, lon in query_result
    ]
    
    return jsonify(daftar_lokasi)
