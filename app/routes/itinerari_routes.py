from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.itinerari import Itinerari
from app.forms import ItinerariForm

itinerari = Blueprint('itinerari', __name__)

@itinerari.route('/itinerari')
def list_itinerari():
    """
    Menampilkan daftar semua itinerari perjalanan yang dibuat pengguna.

    Data diurutkan dari yang terbaru berdasarkan waktu pembuatan.
    Setiap itinerari mencakup judul, pembuat, dan daftar destinasi wisata.
    Dapat diakses oleh semua pengunjung sebagai inspirasi perjalanan.

    Returns:
        Response: Render template 'itinerari/list.html' dengan daftar itinerari.
    """
    semua_itinerari = Itinerari.query.order_by(Itinerari.tanggal_dibuat.desc()).all()

    return render_template('itinerari/list.html', daftar_itinerari=semua_itinerari)

@itinerari.route('/itinerari/detail/<int:id>')
def detail_itinerari(id):
    """
    Menampilkan detail lengkap dari satu itinerari berdasarkan ID.

    Berisi judul, deskripsi opsional, pembuat, dan daftar destinasi wisata
    yang dipilih. Halaman ini menjadi representasi naratif dari rencana
    perjalanan pengguna di Lelana.id.

    Args:
        id (int): ID itinerari yang akan ditampilkan.

    Returns:
        Response: Render template 'itinerari/detail.html' dengan objek itinerari.
    """
    it = Itinerari.query.get_or_404(id)

    return render_template('itinerari/detail.html', itinerari=it)

@itinerari.route('/itinerari/buat', methods=['GET', 'POST'])
@login_required
def buat_itinerari():
    """
    Menangani pembuatan itinerari baru oleh pengguna terautentikasi.

    Saat GET: menampilkan formulir dengan daftar destinasi wisata yang dapat dipilih.
    Saat POST dan valid: menyimpan itinerari ke database dengan relasi many-to-many
    ke destinasi yang dipilih, serta mengaitkannya dengan pengguna saat ini.

    Returns:
        Response: Render formulir buat (GET) atau redirect ke detail itinerari (POST sukses).
    """
    form = ItinerariForm()
    if form.validate_on_submit():
        it_baru = Itinerari(
            judul=form.judul.data,
            deskripsi=form.deskripsi.data,
            penulis=current_user,
            wisata_termasuk=form.wisata_termasuk.data
        )

        db.session.add(it_baru)
        db.session.commit()

        flash('Itinerari Petualangan baru berhasil dibuat!', 'success')
        return redirect(url_for('itinerari.detail_itinerari', id=it_baru.id))
    
    return render_template('itinerari/buat_edit.html', form=form, judul_halaman='Buat Itinerari Baru')

@itinerari.route('/itinerari/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_itinerari(id):
    """
    Menangani pembaruan itinerari yang hanya dapat dilakukan oleh pembuatnya.

    Memverifikasi bahwa pengguna saat ini adalah pemilik itinerari.
    Jika bukan, respons 403 Forbidden dikembalikan. Saat valid, memperbarui
    judul, deskripsi, dan daftar destinasi.

    Args:
        id (int): ID itinerari yang akan diedit.

    Returns:
        Response: Render formulir edit (GET) atau redirect ke detail (POST sukses).
    """
    it = Itinerari.query.get_or_404(id)
    if it.penulis != current_user:
        abort(403)

    form = ItinerariForm(obj=it)
    if form.validate_on_submit():
        it.judul = form.judul.data
        it.deskripsi = form.deskripsi.data
        it.wisata_termasuk = form.wisata_termasuk.data
        db.session.commit()

        flash('Itinerari berhasil diperbarui!', 'success')
        return redirect(url_for('itinerari.detail_itinerari', id=it.id))
    
    return render_template('itinerari/buat_edit.html', form=form, judul_halaman='Edit Itinerari')

@itinerari.route('/itinerari/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_itinerari(id):
    """
    Menghapus itinerari berdasarkan ID, hanya oleh pemiliknya.

    Memastikan bahwa hanya pengguna yang membuat itinerari yang dapat
    menghapusnya. Operasi hanya tersedia via POST untuk keamanan.
    Setelah dihapus, pengguna dialihkan kembali ke daftar itinerari.

    Args:
        id (int): ID itinerari yang akan dihapus.

    Returns:
        Response: Redirect ke daftar itinerari dengan pesan konfirmasi.
    """
    it = Itinerari.query.get_or_404(id)
    if it.penulis != current_user:
        abort(403)

    db.session.delete(it)
    db.session.commit()

    flash('Itinerari telah berhasil dihapus.', 'info')
    return redirect(url_for('itinerari.list_itinerari'))