from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app import db, limiter
from app.models.event import Event
from app.forms import EventForm
from app.utils.decorators import admin_required
from flask_wtf import FlaskForm

event = Blueprint('event', __name__)

@event.route('/event')
def list_event():
    """Menampilkan daftar event dengan pagination.

    Menyajikan event yang diurutkan berdasarkan tanggal pelaksanaan (terbaru di atas),
    dengan 5 item per halaman. Menyertakan formulir hapus untuk keamanan CSRF.

    Returns:
        Response: Render template daftar event dengan data pagination.
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
    """Menampilkan detail lengkap suatu event berdasarkan ID.

    Args:
        id (int): ID unik event yang ingin dilihat.

    Returns:
        Response: Render template detail event jika ditemukan.

    Raises:
        HTTPException: 404 Not Found jika event tidak ada.
    """
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)

    return render_template('event/detail.html', event=event_item)

@event.route('/event/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def tambah_event():
    """Menangani penambahan event baru oleh admin.

    Hanya dapat diakses oleh pengguna terautentikasi dengan peran admin.
    Menggunakan formulir EventForm untuk validasi input.

    Returns:
        Response: Render formulir tambah jika GET, atau redirect ke daftar event jika sukses.
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
@limiter.limit("30 per minute", methods=["POST"])
def edit_event(id):
    """Menangani pembaruan data event oleh admin.

    Memuat data event yang ada ke dalam formulir dan menyimpan perubahan
    setelah validasi berhasil.

    Args:
        id (int): ID event yang akan diedit.

    Returns:
        Response: Render formulir edit jika GET, atau redirect ke detail event jika sukses.

    Raises:
        HTTPException: 404 Not Found jika event tidak ditemukan.
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
@limiter.limit("30 per minute")
def hapus_event(id):
    """Menghapus event dari sistem berdasarkan ID.

    Memerlukan validasi formulir CSRF untuk mencegah serangan cross-site request forgery.
    Hanya dapat diakses oleh admin.

    Args:
        id (int): ID event yang akan dihapus.

    Returns:
        Response: Redirect ke daftar event dengan pesan status operasi.

    Raises:
        HTTPException: 404 Not Found jika event tidak ditemukan.
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