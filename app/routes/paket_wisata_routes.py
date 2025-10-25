from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app, request
from flask_login import login_required, current_user
from app import db, limiter
from app.models.paket_wisata import PaketWisata
from app.forms import PaketWisataForm
from app.utils.decorators import admin_required
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from flask_wtf import FlaskForm

paket_wisata = Blueprint('paket_wisata', __name__)

@paket_wisata.route('/paket-wisata')
def list_paket():
    """Menampilkan daftar semua paket wisata yang tersedia dengan paginasi.

    Data diurutkan berdasarkan nama secara alfabetis dan mencakup formulir hapus
    untuk keamanan CSRF pada operasi penghapusan.

    Returns:
        Response: Render template daftar paket wisata dengan data paginasi.
    """
    page = request.args.get('page', 1, type=int)
    
    # Menggunakan db.paginate untuk efisiensi dan paginasi
    pagination = db.paginate(
        db.select(PaketWisata).order_by(PaketWisata.nama),
        page=page,
        per_page=9,
        error_out=False
    )
    daftar_paket = pagination.items

    delete_form = FlaskForm()

    return render_template('paket_wisata/list.html', 
                           daftar_paket=daftar_paket, 
                           delete_form=delete_form,
                           pagination=pagination
    )

@paket_wisata.route('/paket-wisata/detail/<int:id>')
def detail_paket(id):
    """Menampilkan detail lengkap suatu paket wisata berdasarkan ID.

    Memuat daftar destinasi wisata yang termasuk dalam paket menggunakan
    eager loading untuk menghindari query tambahan.

    Args:
        id (int): ID unik paket wisata yang ingin dilihat.

    Returns:
        Response: Render template detail paket wisata jika ditemukan.

    Raises:
        HTTPException: 404 Not Found jika paket tidak ada.
    """
    stmt = select(PaketWisata).options(joinedload(PaketWisata.destinasi)).where(PaketWisata.id == id)
    paket = db.session.scalar(stmt)
    if paket is None:
        abort(404)

    return render_template('paket_wisata/detail.html', paket=paket)

@paket_wisata.route('/paket-wisata/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def tambah_paket():
    """Menangani penambahan paket wisata baru oleh admin.

    Mengumpulkan data melalui PaketWisataForm, termasuk destinasi yang dipilih
    dan status promosi, lalu menyimpan ke database.

    Returns:
        Response: Render formulir tambah jika GET, atau redirect ke daftar paket jika sukses.
    """
    form = PaketWisataForm()
    if form.validate_on_submit():
        paket_baru = PaketWisata(
            nama=form.nama.data,
            deskripsi=form.deskripsi.data,
            harga=form.harga.data,
            destinasi=form.destinasi.data,
            is_promoted=form.is_promoted.data
        )

        db.session.add(paket_baru)
        db.session.commit()

        current_app.logger.info('Admin %s menambahkan Paket Wisata baru "%s" (ID: %d).', 
            current_user.username, paket_baru.nama, paket_baru.id
        )

        flash('Paket wisata baru berhasil ditambahkan!', 'success')
        return redirect(url_for('paket_wisata.list_paket'))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Tambah Paket Wisata')

@paket_wisata.route('/paket-wisata/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def edit_paket(id):
    """Menangani pembaruan data paket wisata oleh admin.

    Memuat data paket yang ada ke dalam formulir dan menyimpan perubahan
    setelah validasi berhasil.

    Args:
        id (int): ID paket wisata yang akan diedit.

    Returns:
        Response: Render formulir edit jika GET, atau redirect ke detail paket jika sukses.

    Raises:
        HTTPException: 404 Not Found jika paket tidak ditemukan.
    """
    paket = db.session.get(PaketWisata, id)
    if paket is None:
        abort(404)
    form = PaketWisataForm(obj=paket)
    if form.validate_on_submit():
        paket.nama = form.nama.data
        paket.deskripsi = form.deskripsi.data
        paket.harga = form.harga.data
        paket.destinasi = form.destinasi.data
        paket.is_promoted = form.is_promoted.data
        db.session.commit()

        current_app.logger.info('Admin %s memperbarui Paket Wisata "%s" (ID: %d).', 
            current_user.username, paket.nama, paket.id
        )

        flash('Paket wisata berhasil diperbarui!', 'success')
        return redirect(url_for('paket_wisata.detail_paket', id=paket.id))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Edit Paket Wisata')

@paket_wisata.route('/paket-wisata/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_paket(id):
    """Menghapus paket wisata dari sistem berdasarkan ID.

    Memerlukan validasi CSRF melalui formulir kosong. Hanya dapat diakses oleh admin.

    Args:
        id (int): ID paket wisata yang akan dihapus.

    Returns:
        Response: Redirect ke daftar paket dengan pesan status operasi.

    Raises:
        HTTPException: 404 Not Found jika paket tidak ditemukan.
    """
    paket = db.session.get(PaketWisata, id)
    if paket is None:
        abort(404)
    
    form = FlaskForm()
    if form.validate_on_submit():
        current_app.logger.info('Admin %s menghapus Paket Wisata "%s" (ID: %d).', 
            current_user.username, paket.nama, paket.id
        )

        db.session.delete(paket)
        db.session.commit()
        flash('Paket wisata telah berhasil dihapus', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('paket_wisata.list_paket'))