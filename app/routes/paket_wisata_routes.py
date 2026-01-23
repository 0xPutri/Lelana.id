from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app, request
from flask_login import login_required, current_user
from app import db, limiter
from app.models.paket_wisata import PaketWisata
from app.forms import PaketWisataForm
from app.utils.decorators import admin_required
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from flask_wtf import FlaskForm

# Membuat Blueprint untuk rute-rute terkait paket wisata
paket_wisata = Blueprint('paket_wisata', __name__)

@paket_wisata.route('/paket-wisata')
def list_paket():
    """Menampilkan daftar semua paket wisata dengan sistem pagination.

    Returns:
        Response: Render template halaman daftar paket wisata dengan data
                  paket dan kontrol pagination.
    """
    # Mengambil nomor halaman dari query parameter URL, default ke halaman 1
    page = request.args.get('page', 1, type=int)
    
    # Menggunakan db.paginate untuk query yang lebih modern dan efisien
    pagination = db.paginate(
        db.select(PaketWisata).order_by(PaketWisata.nama),
        page=page,
        per_page=9,
        error_out=False
    )
    # Mendapatkan item paket wisata untuk halaman saat ini
    daftar_paket = pagination.items

    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('paket_wisata/list.html', 
                           daftar_paket=daftar_paket, 
                           delete_form=delete_form,
                           pagination=pagination
    )

@paket_wisata.route('/paket-wisata/detail/<int:id>')
def detail_paket(id):
    """Menampilkan halaman detail untuk satu paket wisata spesifik.

    Menggunakan 'eager loading' untuk mengambil data destinasi secara efisien.

    Args:
        id (int): ID dari paket wisata yang akan ditampilkan.

    Returns:
        Response: Render template halaman detail paket wisata.
    """
    # Membuat statement query untuk mengambil paket wisata berdasarkan ID
    # joinedload(PaketWisata.destinasi) memastikan data destinasi diambil dalam query yang sama
    stmt = select(PaketWisata).options(joinedload(PaketWisata.destinasi)).where(PaketWisata.id == id)
    # Mengeksekusi query dan mengambil satu hasil atau None
    paket = db.session.scalar(stmt)
    if paket is None:
        abort(404)

    return render_template('paket_wisata/detail.html', paket=paket)

@paket_wisata.route('/paket-wisata/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def tambah_paket():
    """Menangani pembuatan paket wisata baru oleh admin.

    Menampilkan form untuk membuat paket (GET) dan memproses data
    yang disubmit (POST).

    Returns:
        Response: Render template form, atau redirect ke daftar paket
                  setelah berhasil dibuat.
    """
    form = PaketWisataForm()
    if form.validate_on_submit():
        # Membuat instance PaketWisata baru dari data form
        paket_baru = PaketWisata(
            nama=form.nama.data,
            deskripsi=form.deskripsi.data,
            harga=form.harga.data,
            destinasi=form.destinasi.data,
            is_promoted=form.is_promoted.data
        )

        # Menambahkan dan menyimpan objek ke database
        db.session.add(paket_baru)
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menambahkan Paket Wisata baru "%s" (ID: %d).', 
            current_user.username, paket_baru.nama, paket_baru.id
        )

        flash('Paket wisata baru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.manage_paket_wisata'))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Tambah Paket Wisata')

@paket_wisata.route('/paket-wisata/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def edit_paket(id):
    """Menangani pembaruan paket wisata yang sudah ada oleh admin.

    Menampilkan form yang sudah terisi data (GET) dan memproses
    perubahan yang disubmit (POST).

    Args:
        id (int): ID dari paket wisata yang akan diedit.

    Returns:
        Response: Render template form, atau redirect ke detail paket
                  setelah berhasil diperbarui.
    """
    # Mengambil data paket wisata dari database, atau 404 jika tidak ada
    paket = db.session.get(PaketWisata, id)
    if paket is None:
        abort(404)
    # Menginisialisasi form dengan data dari objek paket wisata
    form = PaketWisataForm(obj=paket)
    if form.validate_on_submit():
        # Memperbarui atribut objek dengan data dari form
        paket.nama = form.nama.data
        paket.deskripsi = form.deskripsi.data
        paket.harga = form.harga.data
        paket.destinasi = form.destinasi.data
        paket.is_promoted = form.is_promoted.data
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s memperbarui Paket Wisata "%s" (ID: %d).', 
            current_user.username, paket.nama, paket.id
        )

        flash('Paket wisata berhasil diperbarui!', 'success')
        return redirect(url_for('admin.manage_paket_wisata'))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Edit Paket Wisata')

@paket_wisata.route('/paket-wisata/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_paket(id):
    """Memproses permintaan penghapusan paket wisata.

    Memerlukan validasi token CSRF sebelum menghapus data.

    Args:
        id (int): ID dari paket wisata yang akan dihapus.

    Returns:
        Response: Redirect ke halaman daftar paket wisata dengan pesan status.
    """
    # Mengambil data paket wisata dari database, atau 404 jika tidak ada
    paket = db.session.get(PaketWisata, id)
    if paket is None:
        abort(404)
    
    # Membuat instance form kosong untuk validasi CSRF
    form = FlaskForm()
    if form.validate_on_submit():
        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menghapus Paket Wisata "%s" (ID: %d).', 
            current_user.username, paket.nama, paket.id
        )

        # Menghapus objek dari database
        db.session.delete(paket)
        db.session.commit()
        flash('Paket wisata telah berhasil dihapus', 'info')
    else:
        # Gagal jika token CSRF tidak valid
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('admin.manage_paket_wisata'))
