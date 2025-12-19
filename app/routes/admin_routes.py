import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app import db, limiter
from app.models.wisata import Wisata
from app.models.user import User
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app.forms import AdminEditUserForm
from flask_wtf import FlaskForm
from sqlalchemy import func

# Membuat Blueprint untuk rute-rute khusus admin
admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """Menampilkan halaman dashboard utama untuk admin.

    Halaman ini mengumpulkan dan menampilkan statistik agregat tentang konten
    dan pengguna di platform, serta visualisasi data aktivitas terkini.

    Returns:
        Response: Render template halaman dashboard admin dengan data statistik.
    """
    # Menghitung total entitas utama
    total_users = db.session.query(func.count(User.id)).scalar()
    total_wisata = db.session.query(func.count(Wisata.id)).scalar()
    total_paket = db.session.query(func.count(PaketWisata.id)).scalar()
    total_event = db.session.query(func.count(Event.id)).scalar()

    # Menyiapkan data untuk grafik aktivitas konten 30 hari terakhir
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query untuk mengambil jumlah konten baru per hari
    wisata_by_day = db.session.query(
            func.date(Wisata.tanggal_dibuat).label('date'), 
            func.count(Wisata.id).label('count')
        ).filter(Wisata.tanggal_dibuat >= thirty_days_ago).group_by('date').all()

    event_by_day = db.session.query(
            func.date(Event.tanggal_dibuat).label('date'), 
            func.count(Event.id).label('count')
        ).filter(Event.tanggal_dibuat >= thirty_days_ago).group_by('date').all()

    paket_by_day = db.session.query(
            func.date(PaketWisata.tanggal_dibuat).label('date'), 
            func.count(PaketWisata.id).label('count')
        ).filter(PaketWisata.tanggal_dibuat >= thirty_days_ago).group_by('date').all()

    # Menggabungkan data dari semua tipe konten
    content_activity = {}
    for row in wisata_by_day + event_by_day + paket_by_day:
        date_str = row.date
        content_activity[date_str] = content_activity.get(date_str, 0) + row.count

    # Mengisi hari-hari tanpa aktivitas dengan nilai 0
    sorted_dates = sorted(content_activity.keys())
    chart_labels = []
    chart_data = []
    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').date()
        end_date = datetime.utcnow().date()
        delta = end_date - start_date
        
        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            chart_labels.append(day.strftime('%b %d'))
            chart_data.append(content_activity.get(day_str, 0))

    # Mengemas semua statistik untuk dikirim ke template
    stats = {
        'total_users': total_users,
        'total_wisata': total_wisata,
        'total_paket': total_paket,
        'total_event': total_event,
        'chart_data': json.dumps({'labels': chart_labels, 'data': chart_data})
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """Menampilkan halaman untuk mengelola semua pengguna terdaftar.

    Mengambil semua data pengguna dari database dan menampilkannya dalam
    sebuah tabel.

    Returns:
        Response: Render template manajemen pengguna dengan data semua pengguna.
    """
    # Mengambil semua pengguna, diurutkan berdasarkan ID
    users = User.query.order_by(User.id).all()

    # Membuat instance form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()
    return render_template('admin/manage_users.html', users=users, delete_form=delete_form)

@admin.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per minute", methods=["POST"])
def edit_user(id):
    """Menampilkan form dan memproses pengeditan data pengguna.

    Admin dapat mengubah username, email, dan peran pengguna lain. Terdapat
    proteksi untuk mencegah admin mengubah perannya sendiri.

    Args:
        id (int): ID dari pengguna yang akan diedit.

    Returns:
        Response: Render template form edit, atau redirect ke halaman manajemen
                  pengguna setelah berhasil.
    """
    # Mengambil data pengguna yang akan diedit atau menampilkan 404 jika tidak ditemukan
    user_to_edit = User.query.filter_by(id=id).first_or_404()
    form = AdminEditUserForm(original_user=user_to_edit)

    # Memproses form jika metode adalah POST dan validasi berhasil
    if form.validate_on_submit():
        # Mencegah admin mengubah perannya sendiri menjadi bukan admin
        if user_to_edit.id == current_user.id and form.role.data != 'admin':
            flash('Anda tidak mengubah peran (role) akun Anda sendiri.', 'danger')
            return redirect(url_for('admin.edit_user', id=id))

        # Memperbarui data pengguna dari form
        user_to_edit.username = form.username.data
        user_to_edit.email = form.email.data
        user_to_edit.role = form.role.data
        db.session.commit()

        flash(f'Data pengguna {user_to_edit.username} berhasil diperbarui.', 'success')
        return redirect(url_for('admin.manage_users'))
    
    # Mengisi form dengan data pengguna yang ada saat metode adalah GET
    form.username.data = user_to_edit.username
    form.email.data = user_to_edit.email
    form.role.data = user_to_edit.role

    return render_template('admin/edit_user.html', form=form, user=user_to_edit)

@admin.route('/admin/users/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("30 per minute")
def hapus_user(id):
    """Memproses permintaan penghapusan pengguna.

    Memvalidasi token CSRF dan menerapkan logika keamanan untuk mencegah
    penghapusan akun sendiri atau admin terakhir.

    Args:
        id (int): ID dari pengguna yang akan dihapus.

    Returns:
        Response: Redirect ke halaman manajemen pengguna dengan pesan status.
    """
    # Mengambil data pengguna yang akan dihapus
    user_to_delete = db.session.get(User, id)
    if user_to_delete is None:
        abort(404)
    # Membuat instance form kosong untuk validasi CSRF
    form = FlaskForm()

    # Memvalidasi token CSRF dari form yang disubmit
    if form.validate_on_submit():
        # Mencegah admin menghapus akunnya sendiri
        if user_to_delete.id == current_user.id:
            flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        # Logika untuk mencegah penghapusan admin terakhir
        if user_to_delete.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                flash('Tidak dapat menghapus admin terakhir. Harus ada setidaknya satu admin.', 'danger')
                return redirect(url_for('admin.manage_users'))

        # Menghapus pengguna dari sesi database dan menyimpan perubahan
        db.session.delete(user_to_delete)
        db.session.commit()
        
        flash(f'Pengguna {user_to_delete.username} telah berhasil dihapus.', 'info')
    else:
        # Gagal jika token CSRF tidak valid
        flash('Gagal menghapus pengguna: Token keamanan tidak valid atau kedaluwarsa.', 'danger')

    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/wisata')
@login_required
@admin_required
def manage_wisata():
    """Menampilkan halaman untuk mengelola semua data tempat wisata.

    Returns:
        Response: Render template manajemen wisata dengan data semua tempat wisata.
    """
    # Mengambil semua data wisata, diurutkan berdasarkan nama
    semua_wisata = Wisata.query.order_by(Wisata.nama).all()

    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('admin/manage_wisata.html', daftar_wisata=semua_wisata, delete_form=delete_form)

@admin.route('/admin/event')
@login_required
@admin_required
def manage_event():
    """Menampilkan halaman untuk mengelola semua data acara (event).

    Returns:
        Response: Render template manajemen event dengan data semua acara.
    """
    # Mengambil semua data event, diurutkan berdasarkan tanggal terbaru
    semua_event = Event.query.order_by(Event.tanggal.desc()).all()

    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('admin/manage_event.html', daftar_event=semua_event, delete_form=delete_form)

@admin.route('/admin/paket-wisata')
@login_required
@admin_required
def manage_paket_wisata():
    """Menampilkan halaman untuk mengelola semua data paket wisata.

    Returns:
        Response: Render template manajemen paket wisata dengan data semua paket.
    """
    # Mengambil semua data paket wisata, diurutkan berdasarkan nama
    semua_paket = PaketWisata.query.order_by(PaketWisata.nama).all()
    
    # Form kosong untuk proteksi CSRF pada tombol hapus
    delete_form = FlaskForm()

    return render_template('admin/manage_paket_wisata.html', daftar_paket=semua_paket, delete_form=delete_form)
