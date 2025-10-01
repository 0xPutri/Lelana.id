from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app import db
from app.models.wisata import Wisata
from app.models.user import User
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app.forms import AdminEditUserForm
from flask_wtf import FlaskForm

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Menampilkan halaman dashboard utama admin Lelana.id.

    Hanya dapat diakses oleh pengguna terautentikasi dengan role 'admin'.
    Berisi ringkasan aktivitas sistem dan navigasi ke fitur manajemen konten.

    Returns:
        Response: Render template 'admin/dashboard.html'.
    """
    return render_template('admin/dashboard.html')

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """
    Menampilkan daftar lengkap pengguna sistem untuk keperluan administrasi.

    Data diurutkan berdasarkan ID secara ascending. Setiap entri dapat dihapus
    atau diedit oleh admin melalui antarmuka yang dilindungi CSRF (formulir kosong
    disertakan untuk operasi hapus aman). Halaman ini menjadi pusat manajemen akun
    di Lelana.id, termasuk verifikasi peran pengguna.

    Returns:
        Response: Render template 'admin/manage_users.html' dengan daftar pengguna
                  dan formulir hapus untuk keamanan operasi administratif.
    """
    users = User.query.order_by(User.id).all()

    delete_form = FlaskForm()
    return render_template('admin/manage_users.html', users=users, delete_form=delete_form)

@admin.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """
    Mengizinkan admin mengedit data pengguna (username, email, role) dengan proteksi logika bisnis.

    Mencegah admin mengubah perannya sendiri menjadi 'user' (untuk menjaga akses).
    Menggunakan formulir khusus dengan validasi keunikan username/email hanya
    jika nilai diubah. Saat GET, formulir diisi dengan data asli; saat POST valid,
    perubahan disimpan ke database.

    Args:
        id (int): ID pengguna yang akan diedit.

    Returns:
        Response: Render formulir edit (GET) atau redirect ke daftar pengguna (POST sukses).
    """
    user_to_edit = User.query.filter_by(id=id).first_or_404()
    form = AdminEditUserForm(original_user=user_to_edit)

    if form.validate_on_submit():
        if user_to_edit.id == current_user.id and form.role.data != 'admin':
            flash('Anda tidak mengubah peran (role) akun Anda sendiri.', 'danger')
            return redirect(url_for('admin.edit_user', id=id))

        user_to_edit.username = form.username.data
        user_to_edit.email = form.email.data
        user_to_edit.role = form.role.data
        db.session.commit()

        flash(f'Data pengguna {user_to_edit.username} berhasil diperbarui.', 'success')
        return redirect(url_for('admin.manage_users'))
    
    form.username.data = user_to_edit.username
    form.email.data = user_to_edit.email
    form.role.data = user_to_edit.role

    return render_template('admin/edit_user.html', form=form, user=user_to_edit)

@admin.route('/admin/users/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_user(id):
    """
    Menghapus akun pengguna dengan validasi keamanan dan aturan bisnis ketat.

    Memastikan tiga kondisi:
    1. Admin tidak dapat menghapus akunnya sendiri,
    2. Tidak boleh menghapus admin terakhir (minimal satu admin harus tersedia),
    3. Permintaan harus valid (termasuk token CSRF).

    Jika salah satu kondisi dilanggar, operasi dibatalkan dengan pesan error.
    Hanya dapat diakses oleh admin melalui metode POST.

    Args:
        id (int): ID pengguna yang akan dihapus.

    Returns:
        Response: Redirect ke daftar pengguna dengan pesan status (sukses/error).
    """
    user_to_delete = db.session.get(User, id)
    if user_to_delete is None:
        abort(404)
    form = FlaskForm()

    if form.validate_on_submit():
        if user_to_delete.id == current_user.id:
            flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        if user_to_delete.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                flash('Tidak dapat menghapus admin terakhir. Harus ada setidaknya satu admin.', 'danger')
                return redirect(url_for('admin.manage_users'))

        db.session.delete(user_to_delete)
        db.session.commit()
        
        flash(f'Pengguna {user_to_delete.username} telah berhasil dihapus.', 'info')
    else:
        flash('Permintaan tidak valid atau sesi telah kedaluwarsa.', 'danger')

    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/wisata')
@login_required
@admin_required
def manage_wisata():
    """
    Menampilkan daftar semua destinasi wisata untuk manajemen konten admin.

    Data diurutkan secara alfabetis berdasarkan nama. Setiap entri dapat dihapus
    atau diedit melalui antarmuka yang dilindungi CSRF (formulir kosong disertakan).
    Halaman ini menjadi titik masuk utama untuk pemeliharaan konten wisata di Banyumas.

    Returns:
        Response: Render template 'admin/manage_wisata.html' dengan daftar wisata
                  dan formulir hapus untuk keamanan operasi administratif.
    """
    semua_wisata = Wisata.query.order_by(Wisata.nama).all()

    delete_form = FlaskForm()

    return render_template('admin/manage_wisata.html', daftar_wisata=semua_wisata, delete_form=delete_form)

@admin.route('/admin/event')
@login_required
@admin_required
def manage_event():
    """
    Menampilkan daftar event budaya untuk pengelolaan agenda lokal oleh admin.

    Data diurutkan dari event terbaru ke terlama berdasarkan tanggal pelaksanaan.
    Setiap entri dilengkapi formulir hapus aman (CSRF-protected) untuk mencegah
    penghapusan tidak sah. Digunakan untuk memastikan akurasi dan kelengkapan
    informasi kegiatan budaya di Jawa Tengah.

    Returns:
        Response: Render template 'admin/manage_event.html' dengan daftar event
                  dan formulir hapus untuk keamanan operasi administratif.
    """
    semua_event = Event.query.order_by(Event.tanggal.desc()).all()

    delete_form = FlaskForm()

    return render_template('admin/manage_event.html', daftar_event=semua_event, delete_form=delete_form)

@admin.route('/admin/paket-wisata')
@login_required
@admin_required
def manage_paket_wisata():
    """
    Menampilkan daftar paket wisata gabungan untuk verifikasi dan pemeliharaan konten.

    Data diurutkan berdasarkan nama secara alfabetis. Setiap paket dapat dihapus
    atau diedit melalui antarmuka yang dilindungi CSRF (formulir kosong disertakan).
    Halaman ini memastikan konsistensi dan kualitas paket perjalanan yang ditawarkan
    kepada pengguna Lelana.id.

    Returns:
        Response: Render template 'admin/manage_paket_wisata.html' dengan daftar paket
                  dan formulir hapus untuk keamanan operasi administratif.
    """
    semua_paket = PaketWisata.query.order_by(PaketWisata.nama).all()
    
    delete_form = FlaskForm()

    return render_template('admin/manage_paket_wisata.html', daftar_paket=semua_paket, delete_form=delete_form)