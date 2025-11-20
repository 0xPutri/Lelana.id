from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db, limiter
from app.models.event import Event
from app.forms import EventForm
from app.utils.decorators import admin_required
from flask_wtf import FlaskForm

# Membuat Blueprint untuk rute-rute terkait event
event = Blueprint('event', __name__)

@event.route('/event')
def list_event():
    """Menampilkan daftar semua event dengan sistem pagination.

    Menyajikan event yang diurutkan berdasarkan tanggal (terbaru lebih dulu).
    Setiap halaman menampilkan 5 event.

    Returns:
        Response: Render template halaman daftar event dengan data event
                  dan kontrol pagination.
    """
    # Mengambil nomor halaman dari query parameter URL, default ke halaman 1
    page = request.args.get('page', 1, type=int)
    # Melakukan query ke database dengan pagination
    pagination = Event.query.order_by(Event.tanggal.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    # Mendapatkan item event untuk halaman saat ini
    daftar_event_halaman_ini = pagination.items

    # Membuat form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('event/list.html', 
                            daftar_event=daftar_event_halaman_ini, 
                            pagination=pagination, 
                            delete_form=delete_form)

@event.route('/event/detail/<int:id>')
def detail_event(id):
    """Menampilkan halaman detail untuk satu event spesifik.

    Args:
        id (int): ID dari event yang akan ditampilkan.

    Returns:
        Response: Render template halaman detail event.
    """
    # Mengambil data event dari database berdasarkan ID, atau 404 jika tidak ada
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)

    return render_template('event/detail.html', event=event_item)

@event.route('/event/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def tambah_event():
    """Menangani pembuatan event baru oleh admin.

    Menampilkan form untuk membuat event (GET) dan memproses data
    yang disubmit (POST).

    Returns:
        Response: Render template form, atau redirect ke daftar event
                  setelah berhasil dibuat.
    """
    form = EventForm()
    # Memproses form jika metode adalah POST dan validasi berhasil
    if form.validate_on_submit():
        # Membuat instance Event baru dari data form
        event_baru = Event(
            nama=form.nama.data,
            tanggal=form.tanggal.data,
            lokasi=form.lokasi.data,
            deskripsi=form.deskripsi.data,
            penyelenggara=form.penyelenggara.data
        )
        # Menambahkan dan menyimpan objek ke database
        db.session.add(event_baru)
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menambahkan Event baru "%s" (ID: %d).', 
            current_user.username, event_baru.nama, event_baru.id
        )
            
        flash('Event baru berhasil ditambahkan!', 'success')
        return redirect(url_for('event.list_event'))
    
    # Menampilkan form jika metode adalah GET
    return render_template('event/tambah_edit.html', form=form, judul_halaman='Tambah Event Baru')

@event.route('/event/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def edit_event(id):
    """Menangani pembaruan data event yang sudah ada oleh admin.

    Menampilkan form yang sudah terisi data event (GET) dan memproses
    perubahan yang disubmit (POST).

    Args:
        id (int): ID dari event yang akan diedit.

    Returns:
        Response: Render template form, atau redirect ke detail event
                  setelah berhasil diperbarui.
    """
    # Mengambil data event yang akan diedit, atau 404 jika tidak ada
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)
    # Menginisialisasi form dengan data dari objek event
    form = EventForm(obj=event_item)
    if form.validate_on_submit():
        # Memperbarui atribut objek dengan data dari form
        event_item.nama = form.nama.data
        event_item.tanggal = form.tanggal.data
        event_item.lokasi = form.lokasi.data
        event_item.deskripsi = form.deskripsi.data
        event_item.penyelenggara = form.penyelenggara.data
        db.session.commit()

        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s memperbarui Event "%s" (ID: %d).', 
            current_user.username, event_item.nama, event_item.id
        )

        flash('Data event berhasil diperbarui!', 'success')
        return redirect(url_for('event.detail_event', id=event_item.id))
    
    # Menampilkan form dengan data yang ada jika metode adalah GET
    return render_template('event/tambah_edit.html', form=form, judul_halaman='Edit Event')

@event.route('/event/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_event(id):
    """Memproses permintaan penghapusan event.

    Memvalidasi token CSRF sebelum menghapus data dari database.

    Args:
        id (int): ID dari event yang akan dihapus.

    Returns:
        Response: Redirect ke halaman daftar event dengan pesan status.
    """
    # Mengambil data event yang akan dihapus, atau 404 jika tidak ada
    event_item = db.session.get(Event, id)
    if event_item is None:
        abort(404)

    # Membuat instance form kosong untuk validasi CSRF
    form = FlaskForm()
    # Memvalidasi token CSRF
    if form.validate_on_submit():
        # Mencatat aktivitas admin
        current_app.logger.info('Admin %s menghapus Event "%s" (ID: %d).', 
            current_user.username, event_item.nama, event_item.id
        )

        # Menghapus objek dari database
        db.session.delete(event_item)
        db.session.commit()
        flash('Event telah berhasil dihapus.', 'info')
    else:
        # Gagal jika token CSRF tidak valid
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('event.list_event'))
