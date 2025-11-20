from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models.user import User
from app.forms import LoginForm, RegistrationForm, PasswordResetForm, PasswordResetRequestForm
from app.services.email_handler import send_email

# Membuat Blueprint untuk rute-rute terkait autentikasi
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour") # Batasi pendaftaran 5 kali per jam per IP
def register():
    """Menangani pendaftaran pengguna baru.

    Fungsi ini memvalidasi data dari form registrasi, membuat pengguna baru,
    mengirim email konfirmasi, dan secara otomatis me-login pengguna tersebut.

    Returns:
        Response: Render template form registrasi, atau redirect ke halaman
                  utama setelah pendaftaran berhasil.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Jika email sudah ada, tidak membuat user baru tapi tetap beri kesan berhasil
        # untuk mencegah enumerasi email.
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email konfirmasi telah dikirim. Silakan periksa email Anda.', 'success')
            return redirect(url_for('main.index'))

        # Membuat instance pengguna baru
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        # Menyetel password (akan di-hash oleh setter di model)
        user.password = form.password.data

        # Menambahkan dan menyimpan pengguna ke database
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('User baru "%s" (%s) telah terdaftar.', user.username, user.email)

        # Membuat token dan mengirim email konfirmasi
        token = user.generate_confirmation_token()
        send_email(user.email, 'Konfirmasi Akun Lelana.id Anda', 
                   'auth/email/confirm', user=user, token=token)
        
        # Langsung login pengguna setelah registrasi
        login_user(user)
        flash('Registrasi berhasil! Email konfirmasi telah dikirim. Silakan periksa email Anda.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
def confirm(token):
    """Memproses token konfirmasi email.

    Jika token valid, status konfirmasi pengguna akan diperbarui. Pengguna
    juga akan di-login jika belum ada sesi aktif.

    Args:
        token (str): Token konfirmasi yang diterima dari URL.

    Returns:
        Response: Redirect ke halaman utama dengan pesan status.
    """
    # Jika pengguna sudah login dan terkonfirmasi, langsung arahkan
    if current_user.is_authenticated and current_user.is_confirmed:
        return redirect(url_for('main.index'))
    
    # Memverifikasi token menggunakan metode statis dari model User
    user = User.confirm(token)
    if user:
        # Menyimpan perubahan status konfirmasi ke database
        db.session.commit()
        # Jika belum ada sesi, login pengguna
        if not current_user.is_authenticated:
            login_user(user)
        flash('Anda telah berhasil mengkonfirmasi akun Anda. Terima kasih!', 'success')
    else:
        # Jika token tidak valid atau kedaluwarsa
        flash('Tautan konfirmasi tidak valid atau telah kedaluwarsa.', 'danger')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    """Middleware yang berjalan sebelum setiap request.

    Fungsi ini memeriksa apakah pengguna sudah login tapi belum mengonfirmasi
    emailnya. Jika ya, pengguna akan diarahkan ke halaman 'unconfirmed'.
    """
    if current_user.is_authenticated \
            and not current_user.is_confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    """Menampilkan halaman pemberitahuan untuk akun yang belum dikonfirmasi.

    Returns:
        Response: Render template halaman 'unconfirmed'.
    """
    # Jika pengguna anonim atau sudah terkonfirmasi, arahkan ke halaman utama
    if current_user.is_anonymous or current_user.is_confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
@limiter.limit("3 per 24 hours")
def resend_confirmation():
    """Mengirim ulang email konfirmasi ke pengguna yang sedang login.

    Dibatasi untuk mencegah spam email.

    Returns:
        Response: Redirect ke halaman utama dengan pesan status.
    """
    # Membuat token baru dan mengirimkannya kembali
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Konfirmasi Akun Lelana.id Anda', 
               'auth/email/confirm', user=current_user, token=token)
    
    flash('Email konfirmasi baru telah dikirimkan.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("100 per day; 20 per hour; 5 per minute")
def login():
    """Menangani proses login pengguna.

    Memvalidasi kredensial dari form login. Jika berhasil, membuat sesi
    login untuk pengguna.

    Returns:
        Response: Render template form login, atau redirect ke halaman utama
                  setelah login berhasil.
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Mencari pengguna berdasarkan email
        user = User.query.filter_by(email=form.email.data).first()
        # Memverifikasi keberadaan pengguna dan kecocokan password
        if user and user.verify_password(form.password.data):
            # Membuat sesi login
            login_user(user, remember=form.remember.data)
            current_app.logger.info('Login berhasil untuk user "%s" dari IP %s.', 
                user.username, request.remote_addr
            )

            flash('Login berhasil!', 'success')
            return redirect(url_for('main.index'))
        else:
            # Jika login gagal
            current_app.logger.warning('Login GAGAL untuk email "%s" dari IP %s.', 
                form.email.data, request.remote_addr
            )
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("3 per 24 hours")
def password_reset_request():
    """Menangani permintaan untuk mereset password.

    Mengirim email berisi token reset jika email pengguna terdaftar.

    Returns:
        Response: Render template form permintaan reset, atau redirect ke
                  halaman login setelah form disubmit.
    """
    # Jika pengguna sudah login, tidak perlu reset password
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Jika pengguna ada, buat token dan kirim email
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Password Akun Lelana.id Anda',
                       'auth/email/reset_password',
                       user=user, token=token)
            
            current_app.logger.info('Email reset password dikirim ke %s.', user.email)
        # Pesan yang ditampilkan sama baik email ada atau tidak, untuk keamanan
        flash('Jika email terdaftar di sistem kami, instruksi reset password telah dikirim.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Memproses reset password menggunakan token.

    Memverifikasi token dan menampilkan form untuk memasukkan password baru.

    Args:
        token (str): Token reset password yang diterima dari URL.

    Returns:
        Response: Render template form reset password, atau redirect ke halaman
                  login jika token tidak valid atau setelah berhasil.
    """
    # Jika pengguna sudah login, tidak perlu reset password
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # Memverifikasi token dan mendapatkan pengguna terkait
    user = User.verify_reset_token(token)
    if not user:
        # Jika token tidak valid atau kedaluwarsa
        flash('Tautan reset password tidak valid atau telah kedaluwarsa.', 'warning')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Menyetel password baru
        user.password = form.password.data
        db.session.commit()

        current_app.logger.info('User %s berhasil mereset password.', user.username)

        flash('Password Anda telah berhasil direset. Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Melakukan logout untuk pengguna yang sedang aktif sesinya.

    Returns:
        Response: Redirect ke halaman utama setelah logout.
    """
    current_app.logger.info('User "%s" telah logout.', current_user.username)
    
    # Menghapus sesi pengguna dari Flask-Login
    logout_user()
    flash('Anda telah berhasil logout.', 'info')

    return redirect(url_for('main.index'))
