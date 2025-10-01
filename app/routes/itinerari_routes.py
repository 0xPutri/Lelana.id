from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.itinerari import Itinerari
from app.forms import ItinerariForm
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm

itinerari = Blueprint('itinerari', __name__)

@itinerari.route('/itinerari')
def list_itinerari():
    """
    Menampilkan daftar semua itinerari perjalanan yang dibuat pengguna.

    Data diurutkan dari yang terbaru berdasarkan waktu pembuatan.
    Setiap entri menyertakan informasi pembuat (penulis) yang dimuat secara
    eager menggunakan joinedload untuk menghindari query tambahan saat render.
    Halaman ini bersifat publik dan berfungsi sebagai galeri inspirasi perjalanan
    berbasis pengalaman nyata pengguna Lelana.id.

    Returns:
        Response: Render template 'itinerari/list.html' dengan daftar itinerari
                  dan data penulis yang telah dipra-muat.
    """
    semua_itinerari = Itinerari.query.options(joinedload(Itinerari.penulis))\
        .order_by(Itinerari.tanggal_dibuat.desc()).all()

    return render_template('itinerari/list.html', daftar_itinerari=semua_itinerari)

@itinerari.route('/itinerari/detail/<int:id>')
def detail_itinerari(id):
    """
    Menampilkan detail lengkap satu itinerari termasuk pembuat dan destinasi terkait.

    Menggunakan optimasi query dengan joinedload untuk memuat relasi ke penulis
    dan daftar destinasi wisata dalam satu permintaan database, mencegah N+1 query.
    Juga menyertakan formulir kosong (FlaskForm) untuk mendukung penghapusan aman
    oleh pemilik melalui POST dengan CSRF protection.

    Args:
        id (int): ID itinerari yang akan ditampilkan.

    Returns:
        Response: Render template 'itinerari/detail.html' dengan data itinerari,
                  penulis, destinasi, dan formulir hapus.
    """
    it = Itinerari.query.options(
        joinedload(Itinerari.penulis), 
        joinedload(Itinerari.wisata_termasuk)
    ).filter_by(id=id).first_or_404()

    delete_form = FlaskForm()

    return render_template('itinerari/detail.html', itinerari=it, delete_form=delete_form)

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
    it = db.session.get(Itinerari, id)
    if it is None:
        abort(404)
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
    Menghapus itinerari berdasarkan ID, hanya oleh pemiliknya, dengan validasi CSRF.

    Memastikan bahwa hanya pengguna yang membuat itinerari yang dapat menghapusnya.
    Operasi hanya diizinkan via POST dan memerlukan formulir valid (termasuk token CSRF)
    untuk mencegah eksekusi tidak sah. Jika validasi gagal, pengguna diberi pesan error.

    Args:
        id (int): ID itinerari yang akan dihapus.

    Returns:
        Response: Redirect ke daftar itinerari dengan pesan sukses jika valid,
                  atau pesan error jika permintaan tidak memenuhi syarat keamanan.
    """
    it = db.session.get(Itinerari, id)
    if it is None:
        abort(404)
    if it.penulis != current_user:
        abort(403)

    form = FlaskForm()
    if form.validate_on_submit():
        db.session.delete(it)
        db.session.commit()
        flash('Itinerari telah berhasil dihapus.', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kadaluwarsa.', 'danger')

    return redirect(url_for('itinerari.list_itinerari'))