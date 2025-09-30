from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app import db
from app.models.event import Event
from app.forms import EventForm
from app.utils.decorators import admin_required
from flask_wtf import FlaskForm

event = Blueprint('event', __name__)

@event.route('/event')
def list_event():
    """
    Menampilkan daftar event budaya lokal dengan paginasi dan formulir hapus aman.

    Data diurutkan dari event terbaru ke terlama berdasarkan tanggal pelaksanaan,
    dengan 5 entri per halaman. Setiap halaman menyertakan formulir kosong (FlaskForm)
    untuk mendukung operasi penghapusan oleh admin melalui POST yang dilindungi CSRF.
    Halaman ini bersifat publik dan menjadi agenda digital kegiatan budaya di Jawa Tengah.

    Returns:
        Response: Render template 'event/list.html' dengan data paginasi event
                  dan formulir hapus untuk keamanan administrasi konten.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.order_by(Event.tanggal.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    daftar_event_halaman_ini = pagination.items

    delete_form = FlaskForm()

    return render_template('event/list.html', 
                            daftar_event=daftar_event_halaman_ini, 
                            pagination=pagination, 
                            delete_form=delete_form)

@event.route('/event/detail/<int:id>')
def detail_event(id):
    """
    Menampilkan informasi lengkap dari satu event berdasarkan ID.

    Berisi nama, tanggal, lokasi, deskripsi, dan penyelenggara (jika ada).
    Halaman ini menjadi sumber utama informasi bagi pengguna yang ingin
    menghadiri atau memahami konteks acara budaya di Jawa Tengah.

    Args:
        id (int): ID event yang akan ditampilkan.

    Returns:
        Response: Render template 'event/detail.html' dengan objek event.
    """
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)

    return render_template('event/detail.html', event=event_item)

@event.route('/event/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_event():
    """
    Menangani penambahan event budaya baru oleh admin.

    Saat GET: menampilkan formulir input data event.
    Saat POST dan valid: menyimpan event ke database dengan tanggal pelaksanaan
    dan informasi pendukung. Hanya dapat diakses oleh pengguna berperan 'admin'.

    Returns:
        Response: Render formulir tambah (GET) atau redirect ke daftar event (POST sukses).
    """
    form = EventForm()
    if form.validate_on_submit():
        event_baru = Event(
            nama=form.nama.data,
            tanggal=form.tanggal.data,
            lokasi=form.lokasi.data,
            deskripsi=form.deskripsi.data,
            penyelenggara=form.penyelenggara.data
        )
        db.session.add(event_baru)
        db.session.commit()
            
        flash('Event baru berhasil ditambahkan!', 'success')
        return redirect(url_for('event.list_event'))
    
    return render_template('event/tambah_edit.html', form=form, judul_halaman='Tambah Event Baru')

@event.route('/event/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(id):
    """
    Menangani pembaruan data event yang sudah terdaftar.

    Memuat event berdasarkan ID, lalu menampilkan formulir terisi saat GET.
    Saat POST dan valid, memperbarui semua field termasuk tanggal dan lokasi.
    Perubahan langsung disimpan ke database dan pengguna dialihkan ke halaman detail.

    Args:
        id (int): ID event yang akan diedit.

    Returns:
        Response: Render formulir edit (GET) atau redirect ke detail event (POST sukses).
    """
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)
    form = EventForm(obj=event_item)
    if form.validate_on_submit():
        event_item.nama = form.nama.data
        event_item.tanggal = form.tanggal.data
        event_item.lokasi = form.lokasi.data
        event_item.deskripsi = form.deskripsi.data
        event_item.penyelenggara = form.penyelenggara.data
        db.session.commit()

        flash('Data event berhasil diperbarui!', 'success')
        return redirect(url_for('event.detail_event', id=event_item.id))
    
    return render_template('event/tambah_edit.html', form=form, judul_halaman='Edit Event')

@event.route('/event/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_event(id):
    """
    Menghapus event dari sistem berdasarkan ID dengan validasi keamanan CSRF.

    Hanya dapat diakses oleh admin dan hanya menerima metode POST. Memerlukan
    formulir valid (termasuk token CSRF) untuk mencegah penghapusan tidak sah
    melalui tautan langsung atau serangan otomatis. Jika validasi gagal,
    pengguna diberi pesan error tanpa mengubah data.

    Args:
        id (int): ID event yang akan dihapus.

    Returns:
        Response: Redirect ke daftar event dengan pesan sukses jika permintaan valid,
                  atau pesan error jika sesi kedaluwarsa atau token tidak sesuai.
    """
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)

    form = FlaskForm()
    if form.validate_on_submit():
        db.session.delete(event_item)
        db.session.commit()
        flash('Event telah berhasil dihapus.', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('event.list_event'))