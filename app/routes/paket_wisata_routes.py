from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.paket_wisata import PaketWisata
from app.forms import PaketWisataForm
from app.utils.decorators import admin_required

paket_wisata = Blueprint('paket_wisata', __name__)

@paket_wisata.route('/paket-wisata')
def list_paket():
    """
    Menampilkan daftar lengkap paket wisata yang tersedia di Lelana.id.

    Data diurutkan berdasarkan nama secara alfabetis untuk memudahkan pencarian.
    Setiap paket mencakup beberapa destinasi wisata dan memiliki harga tetap.
    Dapat diakses oleh semua pengunjung (publik).

    Returns:
        Response: Render template 'paket_wisata/list.html' dengan daftar paket.
    """
    semua_paket = PaketWisata.query.order_by(PaketWisata.nama).all()

    return render_template('paket_wisata/list.html', daftar_paket=semua_paket)

@paket_wisata.route('/paket-wisata/detail/<int:id>')
def detail_paket(id):
    """
    Menampilkan informasi lengkap dari satu paket wisata berdasarkan ID.

    Berisi nama, deskripsi, harga, dan daftar destinasi yang termasuk dalam paket.
    Halaman ini menjadi titik informasi utama bagi pengguna yang ingin memahami
    isi paket sebelum merencanakan perjalanan.

    Args:
        id (int): ID paket wisata yang akan ditampilkan.

    Returns:
        Response: Render template 'paket_wisata/detail.html' dengan objek paket.
    """
    paket = PaketWisata.query.get_or_404(id)

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
    Menghapus paket wisata dari sistem berdasarkan ID.

    Hanya menerima metode POST untuk mencegah penghapusan tidak sengaja.
    Operasi ini juga menghapus relasi ke destinasi terkait secara otomatis
    berkat konfigurasi cascade di model PaketWisata.

    Args:
        id (int): ID paket wisata yang akan dihapus.

    Returns:
        Response: Redirect ke daftar paket dengan pesan konfirmasi.
    """
    paket = PaketWisata.query.get_or_404(id)
    db.session.delete(paket)
    db.session.commit()

    flash('Paket wisata telah berhasil dihapus.', 'info')
    return redirect(url_for('paket_wisata.list_paket'))