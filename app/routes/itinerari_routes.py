from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db, limiter
from app.models.itinerari import Itinerari
from app.forms import ItinerariForm
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm
from app.utils.text_filters import censor_text

itinerari = Blueprint('itinerari', __name__)

@itinerari.route('/itinerari')
def list_itinerari():
    """Menampilkan daftar semua itinerari yang dibuat pengguna.

    Data diurutkan berdasarkan waktu pembuatan (terbaru di atas) dan mencakup
    informasi penulis menggunakan eager loading untuk menghindari N+1 query.

    Returns:
        Response: Render template daftar itinerari.
    """
    semua_itinerari = Itinerari.query.options(joinedload(Itinerari.penulis))\
        .order_by(Itinerari.tanggal_dibuat.desc()).all()

    return render_template('itinerari/list.html', daftar_itinerari=semua_itinerari)

@itinerari.route('/itinerari/detail/<int:id>')
def detail_itinerari(id):
    """Menampilkan detail lengkap suatu itinerari berdasarkan ID.

    Memuat data penulis dan daftar destinasi wisata yang termasuk dalam itinerari
    menggunakan eager loading untuk efisiensi query.

    Args:
        id (int): ID unik itinerari yang ingin dilihat.

    Returns:
        Response: Render template detail itinerari jika ditemukan.

    Raises:
        HTTPException: 404 Not Found jika itinerari tidak ada.
    """
    it = Itinerari.query.options(
        joinedload(Itinerari.penulis), 
        joinedload(Itinerari.wisata_termasuk)
    ).filter_by(id=id).first_or_404()

    delete_form = FlaskForm()

    return render_template('itinerari/detail.html', itinerari=it, delete_form=delete_form)

@itinerari.route('/itinerari/buat', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour", methods=["POST"], key_func=lambda: current_user.id)
def buat_itinerari():
    """Menangani pembuatan itinerari baru oleh pengguna terautentikasi.

    Judul dan deskripsi melewati penyaringan konten (censorship) untuk mencegah
    penggunaan kata tidak pantas. Itinerari dikaitkan dengan pengguna saat ini
    dan destinasi wisata yang dipilih melalui relasi many-to-many.

    Returns:
        Response: Render formulir buat jika GET, atau redirect ke detail itinerari jika sukses.
    """
    form = ItinerariForm()
    if form.validate_on_submit():
        it_baru = Itinerari(
            judul=censor_text(form.judul.data),
            deskripsi=censor_text(form.deskripsi.data),
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
@limiter.limit("20 per hour", methods=["POST"], key_func=lambda: current_user.id)
def edit_itinerari(id):
    """Menangani pembaruan itinerari oleh pemiliknya.

    Memastikan hanya pemilik itinerari yang dapat mengedit. Judul dan deskripsi
    melewati penyaringan konten (censorship) sebelum disimpan. Memperbarui juga
    daftar destinasi wisata yang termasuk dalam itinerari.

    Args:
        id (int): ID itinerari yang akan diedit.

    Returns:
        Response: Render formulir edit jika GET, atau redirect ke detail itinerari jika sukses.

    Raises:
        HTTPException: 404 Not Found jika itinerari tidak ditemukan.
        HTTPException: 403 Forbidden jika pengguna bukan pemilik.
    """
    it = db.session.get(Itinerari, id)
    if it is None:
        abort(404)
    if it.penulis != current_user:
        abort(403)

    form = ItinerariForm(obj=it)
    if form.validate_on_submit():
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
    """Menghapus itinerari dari sistem berdasarkan ID.

    Hanya pemilik itinerari yang diizinkan menghapus. Memerlukan validasi CSRF
    melalui formulir kosong untuk keamanan.

    Args:
        id (int): ID itinerari yang akan dihapus.

    Returns:
        Response: Redirect ke daftar itinerari dengan pesan status operasi.

    Raises:
        HTTPException: 404 Not Found jika itinerari tidak ditemukan.
        HTTPException: 403 Forbidden jika pengguna bukan pemilik.
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