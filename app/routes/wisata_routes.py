from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from app.models.wisata import Wisata
from app.models.review import Review
from app.models.foto_ulasan import FotoUlasan
from app.forms import WisataForm, ReviewForm
from app.utils.decorators import admin_required
from app.services.file_handler import save_pictures
from sqlalchemy.orm import joinedload, subqueryload
from flask_wtf import FlaskForm
from app.utils.text_filters import censor_text

wisata = Blueprint('wisata', __name__)

@wisata.route('/wisata')
def list_wisata():
    """Menampilkan daftar tempat wisata dengan pagination.

    Data diurutkan berdasarkan nama secara alfabetis, dengan 5 item per halaman.
    Menyertakan formulir hapus untuk keamanan CSRF.

    Returns:
        Response: Render template daftar wisata dengan data pagination.
    """
    page = request.args.get('page', 1, type=int)

    pagination = Wisata.query.order_by(Wisata.nama).paginate(
        page=page, per_page=5, error_out=False
    )
    daftar_wisata_halaman_ini = pagination.items

    delete_form = FlaskForm()

    return render_template('wisata/list.html', 
                            daftar_wisata=daftar_wisata_halaman_ini, 
                            pagination=pagination, 
                            delete_form=delete_form)

@wisata.route('/wisata/detail/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per hour", methods=["POST"], key_func=lambda: current_user.id)
def detail_wisata(id):
    """Menampilkan detail tempat wisata dan menangani pengiriman ulasan.

    Memungkinkan pengguna terautentikasi memberikan ulasan dengan komentar yang
    telah melalui penyaringan konten (censorship). Mendukung unggah foto ulasan
    dengan validasi tipe file dan penanganan error yang aman. Data ulasan dimuat
    bersama penulis dan foto menggunakan eager loading untuk efisiensi query.

    Args:
        id (int): ID unik tempat wisata.

    Returns:
        Response: Render template detail wisata dengan formulir ulasan dan daftar ulasan.

    Raises:
        HTTPException: 404 Not Found jika tempat wisata tidak ditemukan.
    """
    w = db.session.get(Wisata, id)
    if w is None:
        abort(404)
    form = ReviewForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        review_baru = Review(
            rating=form.rating.data,
            komentar=censor_text(form.komentar.data),
            author=current_user,
            wisata_reviewed=w
        )
        db.session.add(review_baru)

        if form.foto.data and form.foto.data[0].filename:
            try:
                filenames = save_pictures(form.foto.data)
                for filename in filenames:
                    foto_baru = FotoUlasan(nama_file=filename, review=review_baru)
                    db.session.add(foto_baru)
            except ValueError as e:
                flash(f'Gagal mengunggah: {e}', 'danger')
                db.session.rollback()
                return redirect(url_for('wisata.detail_wisata', id=w.id))
            except Exception as e:
                flash('Terjadi kesalahan internal saat memproses gambar. Silakan coba lagi.', 'danger')
                db.session.rollback()
                return redirect(url_for('wisata.detail_wisata', id=w.id))

        db.session.commit()
        flash('Terima kasih! Review Anda telah ditambahkan.', 'success')
        return redirect(url_for('wisata.detail_wisata', id=w.id))
    
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
    """Menangani penambahan tempat wisata baru oleh admin.

    Mengumpulkan data melalui WisataForm, termasuk koordinat geografis opsional,
    lalu menyimpan ke database.

    Returns:
        Response: Render formulir tambah jika GET, atau redirect ke daftar wisata jika sukses.
    """
    form = WisataForm()
    if form.validate_on_submit():
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

        flash('Destinasi wisata baru berhasil ditambahkan!', 'success')
        return redirect(url_for('wisata.list_wisata'))
    
    return render_template('wisata/tambah_edit.html', form=form, judul_halaman='Tambah Wisata')

@wisata.route('/wisata/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def edit_wisata(id):
    """Menangani pembaruan data tempat wisata oleh admin.

    Memuat data wisata yang ada ke dalam formulir dan menyimpan perubahan,
    termasuk pembaruan koordinat geografis.

    Args:
        id (int): ID tempat wisata yang akan diedit.

    Returns:
        Response: Render formulir edit jika GET, atau redirect ke detail wisata jika sukses.

    Raises:
        HTTPException: 404 Not Found jika tempat wisata tidak ditemukan.
    """
    wisata_item = db.session.get(Wisata, id)
    if wisata_item is None:
        abort(404)
    form = WisataForm(obj=wisata_item)

    if form.validate_on_submit():
        wisata_item.nama = form.nama.data
        wisata_item.kategori = form.kategori.data
        wisata_item.lokasi = form.lokasi.data
        wisata_item.deskripsi = form.deskripsi.data
        wisata_item.gambar_url = form.gambar_url.data
        wisata_item.latitude = form.latitude.data
        wisata_item.longitude = form.longitude.data
        db.session.commit()

        flash('Data wisata berhasil diperbarui!', 'success')
        return redirect(url_for('wisata.detail_wisata', id=wisata_item.id))
    
    return render_template('wisata/tambah_edit.html', form=form, judul_halaman='Edit Wisata')

@wisata.route('/wisata/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_wisata(id):
    """Menghapus tempat wisata dari sistem berdasarkan ID.

    Memerlukan validasi CSRF melalui formulir kosong. Hanya dapat diakses oleh admin.

    Args:
        id (int): ID tempat wisata yang akan dihapus.

    Returns:
        Response: Redirect ke daftar wisata dengan pesan status operasi.

    Raises:
        HTTPException: 404 Not Found jika tempat wisata tidak ditemukan.
    """
    wisata_item = db.session.get(Wisata, id)
    if wisata_item is None: abort(404)
    
    form = FlaskForm()
    if form.validate_on_submit():
        db.session.delete(wisata_item)
        db.session.commit()
        flash('Data wisata telah berhasil dihapus.', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('wisata.list_wisata'))

@wisata.route('/api/wisata/lokasi')
@limiter.limit("60 per minute")
def api_lokasi_wisata():
    """Menyediakan endpoint API untuk mendapatkan lokasi wisata berkoordinat.

    Mengembalikan daftar tempat wisata yang memiliki latitude dan longitude,
    diformat sebagai JSON untuk integrasi dengan peta interaktif.

    Returns:
        Response: JSON berisi daftar lokasi wisata dengan nama, koordinat, dan URL detail.
    """
    query_result = db.session.query(
        Wisata.id,
        Wisata.nama,
        Wisata.latitude,
        Wisata.longitude
    ).filter(Wisata.latitude.isnot(None), Wisata.longitude.isnot(None)).all()

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