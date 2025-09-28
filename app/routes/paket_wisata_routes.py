from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.paket_wisata import PaketWisata
from app.forms import PaketWisataForm
from app.utils.decorators import admin_required
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm

paket_wisata = Blueprint('paket_wisata', __name__)

@paket_wisata.route('/paket-wisata')
def list_paket():
    """
    Menampilkan daftar semua paket wisata dengan formulir hapus aman berbasis CSRF.

    Data diurutkan berdasarkan nama secara alfabetis untuk konsistensi navigasi.
    Setiap entri dapat dihapus oleh admin melalui formulir POST yang dilindungi
    token CSRF (disertakan sebagai objek FlaskForm kosong). Halaman ini bersifat
    publik dan menjadi titik awal eksplorasi paket bagi pengguna umum.

    Returns:
        Response: Render template 'paket_wisata/list.html' dengan daftar paket
                  dan formulir hapus untuk keamanan operasi administratif.
    """
    semua_paket = PaketWisata.query.order_by(PaketWisata.nama).all()

    delete_form = FlaskForm()

    return render_template('paket_wisata/list.html', daftar_paket=semua_paket, delete_form=delete_form)

@paket_wisata.route('/paket-wisata/detail/<int:id>')
def detail_paket(id):
    """
    Menampilkan detail lengkap satu paket wisata termasuk destinasi yang tercakup.

    Menggunakan optimasi query `joinedload` untuk memuat relasi many-to-many
    ke destinasi wisata dalam satu permintaan database, menghindari N+1 query.
    Menampilkan nama, deskripsi, harga, dan daftar destinasi sebagai informasi
    inti bagi pengguna yang ingin memahami cakupan paket perjalanan.

    Args:
        id (int): ID paket wisata yang akan ditampilkan.

    Returns:
        Response: Render template 'paket_wisata/detail.html' dengan data paket
                  dan destinasi terkait yang telah dipra-muat (eager-loaded).
    """
    paket = PaketWisata.query.options(joinedload(PaketWisata.destinasi)).get_or_404(id)

    return render_template('paket_wisata/detail.html', paket=paket)

@paket_wisata.route('/paket-wisata/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_paket():
    """
    Menangani pembuatan paket wisata baru oleh admin.

    Saat GET: menampilkan formulir dengan daftar destinasi yang dapat dipilih.
    Saat POST dan valid: menyimpan paket ke database dengan relasi many-to-many
    ke destinasi yang dipilih. Hanya dapat diakses oleh admin.

    Returns:
        Response: Render formulir tambah (GET) atau redirect ke daftar (POST sukses).
    """
    form = PaketWisataForm()
    if form.validate_on_submit():
        paket_baru = PaketWisata(
            nama=form.nama.data,
            deskripsi=form.deskripsi.data,
            harga=form.harga.data,
            destinasi=form.destinasi.data
        )

        db.session.add(paket_baru)
        db.session.commit()

        flash('Paket wisata baru berhasil ditambahkan!', 'success')
        return redirect(url_for('paket_wisata.list_paket'))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Tambah Paket Wisata')

@paket_wisata.route('/paket-wisata/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_paket(id):
    """
    Menangani pembaruan data paket wisata yang sudah ada.

    Memuat paket berdasarkan ID, lalu menampilkan formulir terisi saat GET.
    Saat POST dan valid, memperbarui nama, deskripsi, harga, dan daftar destinasi.
    Perubahan langsung disimpan ke database.

    Args:
        id (int): ID paket wisata yang akan diedit.

    Returns:
        Response: Render formulir edit (GET) atau redirect ke detail paket (POST sukses).
    """
    paket = PaketWisata.query.get_or_404(id)
    form = PaketWisataForm(obj=paket)
    if form.validate_on_submit():
        paket.nama = form.nama.data
        paket.deskripsi = form.deskripsi.data
        paket.harga = form.harga.data
        paket.destinasi = form.destinasi.data
        db.session.commit()

        flash('Paket wisata berhasil diperbarui!', 'success')
        return redirect(url_for('paket_wisata.detail_paket', id=paket.id))
    
    return render_template('paket_wisata/tambah_edit.html', form=form, judul_halaman='Edit Paket Wisata')

@paket_wisata.route('/paket-wisata/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_paket(id):
    """
    Menghapus paket wisata dari sistem dengan validasi keamanan CSRF.

    Hanya menerima metode POST dan memerlukan formulir valid (termasuk token CSRF)
    untuk mencegah eksekusi tidak sah melalui tautan langsung atau skrip otomatis.
    Operasi hanya dapat dilakukan oleh admin, dan relasi ke destinasi dihapus
    secara otomatis berkat konfigurasi cascade di model.

    Args:
        id (int): ID paket wisata yang akan dihapus.

    Returns:
        Response: Redirect ke daftar paket dengan pesan sukses jika valid,
                  atau pesan error jika permintaan tidak memenuhi syarat keamanan.
    """
    paket = PaketWisata.query.get_or_404(id)
    
    form = FlaskForm()
    if form.validate_on_submit():
        db.session.delete(paket)
        db.session.commit()
        flash('Paket wisata telah berhasil dihapus', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('paket_wisata.list_paket'))