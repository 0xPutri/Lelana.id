from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models.user import User
from app.forms import LoginForm, RegistrationForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Menangani pendaftaran akun pengguna baru di Lelana.id.

    Saat metode GET: menampilkan formulir registrasi.
    Saat metode POST dan data valid: membuat akun pengguna baru, menyimpan ke
    database dengan password dalam bentuk hash, lalu mengarahkan ke halaman login.
    Validasi keunikan username dan email dilakukan secara otomatis oleh formulir.

    Returns:
        Response: Render template registrasi (GET) atau redirect ke login (POST sukses).
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        flash('Selamat! Akun Anda berhasil dibuat. Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Menangani proses login pengguna yang telah terdaftar.

    Saat metode GET: menampilkan formulir login.
    Saat metode POST: memverifikasi kredensial (email + password). Jika valid,
    pengguna diautentikasi melalui Flask-Login dan sesi dimulai. Opsi "Ingat Saya"
    mempertahankan sesi antar kunjungan. Jika gagal, ditampilkan pesan error.

    Returns:
        Response: Render template login (GET atau gagal) atau redirect ke beranda (sukses).
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)

            flash('Login berhasil!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    Mengakhiri sesi pengguna yang sedang aktif.

    Hanya dapat diakses oleh pengguna terautentikasi (dilindungi oleh @login_required).
    Memanggil logout_user() dari Flask-Login untuk membersihkan sesi, lalu
    mengarahkan kembali ke halaman utama dengan pesan konfirmasi.

    Returns:
        Response: Redirect ke halaman utama (main.index) setelah logout.
    """
    logout_user() # Fungsi ini dari Flask-Login, akan menghapus user dari session
    flash('Anda telah berhasil logout.', 'info')

    return redirect(url_for('main.index'))