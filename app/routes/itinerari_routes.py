from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db, limiter
from app.models.itinerari import Itinerari
from app.forms import ItinerariForm
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm
from app.utils.text_filters import censor_text

# Membuat Blueprint untuk rute-rute terkait itinerari
itinerari = Blueprint('itinerari', __name__)

@itinerari.route('/itinerari')
def list_itinerari():
    """Menampilkan daftar semua itinerari yang telah dibuat.

    Menggunakan 'eager loading' (joinedload) untuk mengambil data penulis
    secara efisien dan menghindari N+1 query problem.

    Returns:
        Response: Render template halaman daftar itinerari.
    """
    # Query semua itinerari, diurutkan dari yang terbaru
    # joinedload(Itinerari.penulis) memastikan data penulis (user) diambil dalam query yang sama
    semua_itinerari = Itinerari.query.options(joinedload(Itinerari.penulis))\
        .order_by(Itinerari.tanggal_dibuat.desc()).all()

    return render_template('itinerari/list.html', daftar_itinerari=semua_itinerari)

@itinerari.route('/itinerari/detail/<int:id>')
def detail_itinerari(id):
    """Menampilkan halaman detail untuk satu itinerari spesifik.

    Menggunakan 'eager loading' untuk data penulis dan daftar wisata.

    Args:
        id (int): ID dari itinerari yang akan ditampilkan.

    Returns:
        Response: Render template halaman detail itinerari.
    """
    # Mengambil itinerari berdasarkan ID, termasuk data penulis dan wisata terkait dalam satu query
    it = Itinerari.query.options(
        joinedload(Itinerari.penulis), 
        joinedload(Itinerari.wisata_termasuk)
    ).filter_by(id=id).first_or_404()

    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('itinerari/detail.html', itinerari=it, delete_form=delete_form)

@itinerari.route('/itinerari/buat', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour", methods=["POST"], key_func=lambda: current_user.id)
def buat_itinerari():
    """Menangani pembuatan itinerari baru oleh pengguna.

    Data input dari form akan disensor sebelum disimpan ke database.

    Returns:
        Response: Render template form, atau redirect ke halaman detail
                  setelah berhasil dibuat.
    """
    form = ItinerariForm()
    if form.validate_on_submit():
        # Membuat instance Itinerari baru
        it_baru = Itinerari(
            # Menyensor judul dan deskripsi untuk keamanan
            judul=censor_text(form.judul.data),
            deskripsi=censor_text(form.deskripsi.data),
            # Mengaitkan itinerari dengan pengguna yang sedang login
            penulis=current_user,
            # Mengaitkan dengan daftar wisata yang dipilih (relasi many-to-many)
            wisata_termasuk=form.wisata_termasuk.data
        )

        db.session.add(it_baru)
        db.session.commit()

        flash('Itinerari Petualangan baru berhasil dibuat!', 'success')
        return redirect(url_for('itinerari.detail_itinerari', id=it_baru.id))
    
    return render_template('itinerari/buat_edit.html', form=form, judul_halaman='Buat Itinerari Baru')

@itinerari.route('/itinerari/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour", methods=["POST"], key_func=lambda: current_user.id)
def edit_itinerari(id):
    """Menangani pembaruan itinerari yang sudah ada.

    Hanya pemilik asli yang dapat mengedit itinerarinya.

    Args:
        id (int): ID dari itinerari yang akan diedit.

    Returns:
        Response: Render template form, atau redirect ke halaman detail
                  setelah berhasil diperbarui.
    """
    # Mengambil data itinerari dari database
    it = db.session.get(Itinerari, id)
    if it is None:
        abort(404)
    # Otorisasi: memastikan hanya pemilik yang bisa mengedit
    if it.penulis != current_user:
        abort(403)

    # Menginisialisasi form dengan data dari objek itinerari
    form = ItinerariForm(obj=it)
    if form.validate_on_submit():
        # Memperbarui atribut objek dengan data dari form yang sudah disensor
        it.judul = censor_text(form.judul.data)
        it.deskripsi = censor_text(form.deskripsi.data)
        it.wisata_termasuk = form.wisata_termasuk.data
        db.session.commit()

        flash('Itinerari berhasil diperbarui!', 'success')
        return redirect(url_for('itinerari.detail_itinerari', id=it.id))
    
    return render_template('itinerari/buat_edit.html', form=form, judul_halaman='Edit Itinerari')

@itinerari.route('/itinerari/hapus/<int:id>', methods=['POST'])
@login_required
@limiter.limit("20 per hour", key_func=lambda: current_user.id)
def hapus_itinerari(id):
    """Memproses permintaan penghapusan itinerari.

    Hanya pemilik asli yang dapat menghapus dan memerlukan validasi CSRF.

    Args:
        id (int): ID dari itinerari yang akan dihapus.

    Returns:
        Response: Redirect ke halaman daftar itinerari dengan pesan status.
    """
    # Mengambil data itinerari dari database
    it = db.session.get(Itinerari, id)
    if it is None:
        abort(404)
    # Otorisasi: memastikan hanya pemilik yang bisa menghapus
    if it.penulis != current_user:
        abort(403)

    # Membuat instance form kosong untuk validasi CSRF
    form = FlaskForm()
    if form.validate_on_submit():
        # Menghapus objek dari database
        db.session.delete(it)
        db.session.commit()
        flash('Itinerari telah berhasil dihapus.', 'info')
    else:
        # Gagal jika token CSRF tidak valid
        flash('Permintaan tidak valid atau sesi telah kadaluwarsa.', 'danger')

    return redirect(url_for('itinerari.list_itinerari'))
