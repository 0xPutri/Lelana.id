import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, current_app, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from importlib import import_module

# Inisialisasi ekstensi global untuk digunakan di seluruh aplikasi
db = SQLAlchemy()
login_manager = LoginManager()
# Mengarahkan pengguna ke halaman login jika mencoba mengakses halaman yang dilindungi
login_manager.login_view = 'auth.login'
# Mengatur tingkat proteksi sesi untuk mencegah pencurian sesi
login_manager.session_protection = 'strong'

# Inisialisasi rate limiter untuk membatasi jumlah permintaan
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
# Inisialisasi ekstensi untuk pengiriman email
mail = Mail()
# Inisialisasi proteksi terhadap serangan Cross-Site Request Forgery (CSRF)
csrf = CSRFProtect()

def create_app(config_name):
    """Membuat dan mengonfigurasi instance aplikasi Flask.

    Factory function ini menginisialisasi aplikasi dan semua ekstensinya,
    mendaftarkan blueprint, serta menerapkan konfigurasi spesifik lingkungan.

    Args:
        config_name (str): Nama konfigurasi ('development', 'production', dll.).

    Returns:
        Flask: Instance aplikasi Flask yang telah dikonfigurasi.
    """
    # Membuat instance aplikasi Flask
    app = Flask(__name__)
    # Memuat konfigurasi dari objek berdasarkan nama yang diberikan
    app.config.from_object(config[config_name])

    # Mengimpor dan menginisialisasi filter kustom untuk template Jinja
    from .utils.text_filters import init_profanity_filter, markdown_to_html
    init_profanity_filter(app)
    app.jinja_env.filters['markdown'] = markdown_to_html

    # Menginisialisasi ekstensi dengan instance aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Menerapkan header keamanan pada setiap respons setelah request selesai
    app.after_request(apply_security_headers)

    # Konfigurasi logging untuk lingkungan produksi
    if not app.debug and not app.testing:
        # Membuat direktori log jika belum ada
        if not os.path.exists('logs'):
            os.mkdir('logs')
        # Mengatur file handler untuk rotasi log agar tidak membebani disk
        file_handler = RotatingFileHandler('logs/lelana.log', maxBytes=10240, backupCount=10, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Lelana.id startup in %s mode.', config_name)

    # Mengimpor model User untuk digunakan oleh user_loader
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        """Callback untuk memuat pengguna dari ID yang disimpan di sesi.

        Args:
            user_id (str): ID pengguna yang akan dimuat.

        Returns:
            User | None: Objek pengguna jika ditemukan, atau None jika tidak.
        """
        return db.session.get(User, int(user_id))

    # Mendaftarkan semua blueprint rute ke aplikasi
    register_blueprints(app)

    @app.context_processor
    def inject_now():
        """Menyuntikkan variabel 'now' ke dalam semua konteks template.

        Returns:
            dict: Dictionary berisi objek datetime UTC saat ini.
        """
        return {'now': datetime.utcnow()}

    # Optimasi spesifik untuk database SQLite untuk meningkatkan kinerja konkuren
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite') and ':memory:' not in db_uri:
        with app.app_context():
            engine = db.engine
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """Mengatur PRAGMA untuk koneksi SQLite.

                Args:
                    dbapi_connection: Koneksi DBAPI mentah.
                    connection_record: Catatan koneksi internal SQLAlchemy.
                """
                cursor = dbapi_connection.cursor()
                try:
                    # Mengaktifkan mode Write-Ahead Logging untuk performa tulis yang lebih baik
                    cursor.execute("PRAGMA journal_mode=WAL")
                    # Menetapkan timeout untuk mengatasi database lock
                    cursor.execute("PRAGMA busy_timeout = 5000")
                finally:
                    cursor.close()

    return app

def apply_security_headers(response):
    """Menerapkan header keamanan HTTP dasar pada respons.

    Header ini membantu melindungi aplikasi dari serangan umum seperti clickjacking,
    MIME-type sniffing, dan memastikan koneksi aman melalui HTTPS.

    Args:
        response (Response): Objek respons Flask yang akan dimodifikasi.

    Returns:
        Response: Objek respons Flask dengan header keamanan yang ditambahkan.
    """
    # Memaksa penggunaan HTTPS di lingkungan produksi
    if not current_app.debug and request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Mencegah halaman ditampilkan dalam frame atau iframe di domain lain (Clickjacking)
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    # Mencegah browser dari menebak tipe konten (MIME sniffing)
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Mengontrol informasi referrer yang dikirim saat navigasi
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

def register_blueprints(app):
    """Mendaftarkan semua blueprint rute ke aplikasi secara dinamis.

    Fungsi ini mencari dan mendaftarkan semua blueprint dari modul rute
    untuk menjaga kerapian dan modularitas kode.

    Args:
        app (Flask): Instance aplikasi Flask tempat blueprint akan didaftarkan.
    """
    # Daftar blueprint yang akan didaftarkan: (nama_modul, nama_blueprint, url_prefix)
    blueprints = [
        ('main_routes', 'main', None),
        ('auth_routes', 'auth', '/auth'),
        ('wisata_routes', 'wisata', None),
        ('event_routes', 'event', None),
        ('paket_wisata_routes', 'paket_wisata', None),
        ('itinerari_routes', 'itinerari', None),
        ('admin_routes', 'admin', None),
        ('error_routes', 'errors', None),
        ('chatbot_routes', 'chatbot', None),
    ]

    # Melakukan iterasi dan mendaftarkan setiap blueprint
    for module_name, bp_name, prefix in blueprints:
        # Mengimpor modul rute secara dinamis
        module = import_module(f'.routes.{module_name}', package=__package__)
        # Mendapatkan objek blueprint dari modul
        blueprint = getattr(module, bp_name)
        # Mendaftarkan blueprint ke aplikasi dengan prefix URL jika ada
        app.register_blueprint(blueprint, url_prefix=prefix)