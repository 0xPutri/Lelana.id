from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models.user import User
from app.forms import LoginForm, RegistrationForm, PasswordResetForm, PasswordResetRequestForm
from app.services.email_handler import send_email

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour") # Batasi pendaftaran 5 kali per jam per IP
def register():
    """Menangani pendaftaran pengguna baru dengan pembatasan laju dan konfirmasi email.

    Pengguna yang mendaftar akan dibuat, diautentikasi secara otomatis, dan menerima
    email konfirmasi. Akses dibatasi maksimal 5 pendaftaran per jam per alamat IP.

    Returns:
        Response: Redirect ke halaman utama jika sukses, atau render formulir registrasi.
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
        current_app.logger.info('User baru "%s" (%s) telah terdaftar.', user.username, user.email)

        token = user.generate_confirmation_token()
        send_email(user.email, 'Konfirmasi Akun Lelana.id Anda', 
                   'auth/email/confirm', user=user, token=token)
        
        login_user(user)
        flash('Registrasi berhasil! Email konfirmasi telah dikirim. Silakan periksa email Anda.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
def confirm(token):
    """Memverifikasi token konfirmasi email dan mengaktifkan akun pengguna.

    Jika token valid dan belum kedaluwarsa, status `is_confirmed` pengguna diubah
    menjadi True. Pengguna otomatis login jika belum terautentikasi.

    Args:
        token (str): Token konfirmasi unik yang dikirim melalui email.

    Returns:
        Response: Redirect ke halaman utama dengan pesan sukses atau error.
    """
    if current_user.is_authenticated and current_user.is_confirmed:
        return redirect(url_for('main.index'))
    
    user = User.confirm(token)
    if user:
        db.session.commit()
        if not current_user.is_authenticated:
            login_user(user)
        flash('Anda telah berhasil mengkonfirmasi akun Anda. Terima kasih!', 'success')
    else:
        flash('Tautan konfirmasi tidak valid atau telah kedaluwarsa.', 'danger')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    """Memaksa pengguna yang belum mengonfirmasi email untuk mengakses halaman konfirmasi.

    Middleware ini mencegah akses ke seluruh rute (kecuali blueprint 'auth' dan static)
    jika pengguna sudah login tetapi belum mengonfirmasi alamat emailnya.
    """
    if current_user.is_authenticated \
            and not current_user.is_confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    """Menampilkan halaman pemberitahuan untuk pengguna yang belum mengonfirmasi email.

    Hanya tersedia untuk pengguna terautentikasi yang status konfirmasinya masih False.

    Returns:
        Response: Render halaman unconfirmed.html atau redirect ke index jika tidak relevan.
    """
    if current_user.is_anonymous or current_user.is_confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
@limiter.limit("3 per 24 hours")
def resend_confirmation():
    """Mengirim ulang email konfirmasi akun kepada pengguna yang sudah login.

    Dibatasi maksimal 3 permintaan dalam 24 jam per pengguna untuk mencegah penyalahgunaan.

    Returns:
        Response: Redirect ke halaman utama dengan notifikasi pengiriman email.
    """
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Konfirmasi Akun Lelana.id Anda', 
               'auth/email/confirm', user=current_user, token=token)
    
    flash('Email konfirmasi baru telah dikirimkan.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("100 per day; 20 per hour; 5 per minute")
def login():
    """Menangani proses login pengguna dengan validasi kredensial dan rate limiting.

    Memverifikasi email dan password, lalu mengautentikasi pengguna jika valid.
    Dibatasi maksimal 5 percobaan login per menit per alamat IP.

    Returns:
        Response: Redirect ke halaman utama jika login sukses, atau render formulir login.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            current_app.logger.info('Login berhasil untuk user "%s" dari IP %s.', 
                user.username, request.remote_addr
            )

            flash('Login berhasil!', 'success')
            return redirect(url_for('main.index'))
        else:
            current_app.logger.warning('Login GAGAL untuk email "%s" dari IP %s.', 
                form.email.data, request.remote_addr
            )
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("3 per 24 hours")
def password_reset_request():
    """Menangani permintaan pengguna untuk mereset password yang lupa.

    Jika email ditemukan, sistem mengirim tautan reset ke alamat tersebut.
    Pengguna yang sudah login diarahkan ke halaman utama.

    Returns:
        Response: Render formulir permintaan reset jika GET, atau redirect ke login setelah pengiriman email.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Password Akun Lelana.id Anda',
                       'auth/email/reset_password',
                       user=user, token=token)
            
            current_app.logger.info('Email reset password dikirim ke %s.', user.email)
            flash('Jika email terdaftar di sistem kami, instruksi reset password telah dikirim.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Menangani reset password berdasarkan token yang dikirim melalui email.

    Memverifikasi token, lalu memungkinkan pengguna menetapkan password baru.
    Token yang tidak valid atau kedaluwarsa akan mengarahkan ke halaman login.

    Args:
        token (str): Token reset password unik dari email.

    Returns:
        Response: Render formulir reset password jika token valid, atau redirect ke login jika tidak.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Tautan reset password tidak valid atau telah kedaluwarsa.', 'warning')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()

        current_app.logger.info('User %s berhasil mereset password.', user.username)

        flash('Password Anda telah berhasil direset. Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Melakukan logout pengguna yang sedang login.

    Menghapus sesi pengguna dan menampilkan pesan konfirmasi.

    Returns:
        Response: Redirect ke halaman utama setelah logout.
    """
    current_app.logger.info('User "%s" telah logout.', current_user.username)
    
    logout_user() # Fungsi ini dari Flask-Login, akan menghapus user dari session
    flash('Anda telah berhasil logout.', 'info')

    return redirect(url_for('main.index'))