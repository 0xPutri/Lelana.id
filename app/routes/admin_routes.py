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
    """Menampilkan dashboard admin yang hanya dapat diakses oleh pengguna dengan peran 'admin'.

    Memerlukan autentikasi dan otorisasi khusus admin.

    Returns:
        Response: Render template dashboard admin.
    """
    return render_template('admin/dashboard.html')

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """Menampilkan daftar semua pengguna sistem untuk dikelola oleh admin.

    Returns:
        Response: Render halaman manajemen pengguna dengan daftar pengguna dan formulir hapus.
    """
    users = User.query.order_by(User.id).all()

    delete_form = FlaskForm()
    return render_template('admin/manage_users.html', users=users, delete_form=delete_form)

@admin.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Mengizinkan admin mengedit profil pengguna lain, termasuk username, email, dan peran.

    Mencegah perubahan peran admin pada akun sendiri dan memastikan validasi unik pada
    username dan email.

    Args:
        id (int): ID pengguna yang akan diedit.

    Returns:
        Response: Render formulir edit jika GET, atau redirect ke daftar pengguna jika sukses.
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
    """Menghapus pengguna dari sistem dengan validasi keamanan.

    Mencegah penghapusan akun sendiri dan memastikan setidaknya satu admin tetap ada.
    Menggunakan formulir CSRF untuk keamanan POST request.

    Args:
        id (int): ID pengguna yang akan dihapus.

    Returns:
        Response: Redirect ke daftar pengguna dengan pesan status operasi.
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
    """Menampilkan daftar semua tempat wisata untuk dikelola oleh admin.

    Data diurutkan berdasarkan nama secara alfabetis.

    Returns:
        Response: Render halaman manajemen tempat wisata dengan daftar dan formulir hapus.
    """
    semua_wisata = Wisata.query.order_by(Wisata.nama).all()

    delete_form = FlaskForm()

    return render_template('admin/manage_wisata.html', daftar_wisata=semua_wisata, delete_form=delete_form)

@admin.route('/admin/event')
@login_required
@admin_required
def manage_event():
    """Menampilkan daftar semua acara (event) untuk dikelola oleh admin.

    Data diurutkan berdasarkan tanggal pelaksanaan secara menurun (terbaru di atas).

    Returns:
        Response: Render halaman manajemen acara dengan daftar dan formulir hapus.
    """
    semua_event = Event.query.order_by(Event.tanggal.desc()).all()

    delete_form = FlaskForm()

    return render_template('admin/manage_event.html', daftar_event=semua_event, delete_form=delete_form)

@admin.route('/admin/paket-wisata')
@login_required
@admin_required
def manage_paket_wisata():
    """Menampilkan daftar semua paket wisata untuk dikelola oleh admin.

    Data diurutkan berdasarkan nama secara alfabetis.

    Returns:
        Response: Render halaman manajemen paket wisata dengan daftar dan formulir hapus.
    """
    semua_paket = PaketWisata.query.order_by(PaketWisata.nama).all()
    
    delete_form = FlaskForm()

    return render_template('admin/manage_paket_wisata.html', daftar_paket=semua_paket, delete_form=delete_form)