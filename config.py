import os
from dotenv import load_dotenv

# Menentukan direktori dasar proyek
basedir = os.path.abspath(os.path.dirname(__file__))
# Memuat variabel lingkungan dari file .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Kelas dasar konfigurasi aplikasi dengan pengaturan umum.

    Kelas ini mendefinisikan semua variabel konfigurasi default yang dapat
    di-override oleh kelas turunan untuk lingkungan yang berbeda.

    Attributes:
        WTF_CSRF_ENABLED (bool): Mengaktifkan proteksi CSRF.
        SECRET_KEY (str): Kunci rahasia untuk sesi dan keamanan CSRF.
        SQLALCHEMY_DATABASE_URI (str): URI koneksi database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Nonaktifkan pelacakan modifikasi SQLAlchemy.
        UPLOAD_FOLDER (str): Direktori penyimpanan file yang diunggah.
        ALLOWED_EXTENSIONS (set): Ekstensi file yang diizinkan untuk diunggah.
        MAX_CONTENT_LENGTH (int): Batas ukuran unggahan (dalam byte).
        MAIL_SERVER (str): Server SMTP untuk pengiriman email.
        MAIL_PORT (int): Port server email.
        MAIL_USE_TLS (bool): Aktifkan TLS untuk koneksi email.
        MAIL_USE_SSL (bool): Aktifkan SSL untuk koneksi email.
        MAIL_USERNAME (str): Username autentikasi email.
        MAIL_PASSWORD (str): Password autentikasi email.
        MAIL_SENDER (tuple): Identitas pengirim email default.
        BAD_WORDS_ID (list): Daftar kata terlarang untuk filtering konten.
        ALLOWED_EMAIL_DOMAINS (list): Domain email yang diizinkan.
        GEMINI_API_KEY (str): Kunci API untuk layanan Google Gemini.
    """
    # Mengaktifkan proteksi CSRF secara default
    WTF_CSRF_ENABLED = True

    @staticmethod
    def init_app(app):
        """Metode placeholder untuk inisialisasi tambahan spesifik aplikasi.

        Dapat di-override oleh subclass untuk menyesuaikan perilaku berdasarkan
        lingkungan. Saat ini tidak melakukan apa pun.

        Args:
            app (Flask): Instance aplikasi Flask.
        """
        pass

    # Kunci rahasia untuk keamanan sesi dan token
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Konfigurasi database, menggunakan DATABASE_URL jika ada, jika tidak, default ke SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lelana.db')
    # Menonaktifkan event system SQLAlchemy yang tidak dibutuhkan untuk menghemat resource
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi untuk unggah file
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # Batas ukuran file 10MB

    # Konfigurasi email untuk fitur seperti konfirmasi akun dan reset password
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = ('Tim Lelana.id', os.environ.get('MAIL_USERNAME'))

    # Daftar kata-kata kasar dalam Bahasa Indonesia untuk filter konten
    _bad_words_str = os.environ.get('BAD_WORDS_ID', '')
    BAD_WORDS_ID = [word.strip() for word in _bad_words_str.split(',') if word.strip()]

    # Daftar domain email yang diizinkan untuk pendaftaran
    _allowed_domains_str = os.environ.get('ALLOWED_EMAIL_DOMAINS', 'gmail.com,hotmail.com,outlook.com,yahoo.com,ymail.com,live.com,icloud.com,me.com,mac.com,aol.com,protonmail.com,tutanota.com,zoho.com,gmx.com,mail.com,yandex.com,fastmail.com,hey.com,duck.com,inbox.com,hushmail.com,msn.com,qq.com,163.com,126.com,pm.me,proton.me,lelana.my.id')
    ALLOWED_EMAIL_DOMAINS = [domain.strip() for domain in _allowed_domains_str.split(',') if domain.strip()]

    # Kunci API untuk layanan eksternal
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan pengembangan.

    Mengaktifkan mode debug untuk memudahkan pengembangan lokal dengan fitur
    seperti auto-reloader dan debugger interaktif.
    """
    DEBUG = True

class TestingConfig(Config):
    """Konfigurasi untuk lingkungan pengujian otomatis.

    Menonaktifkan fitur yang dapat mengganggu pengujian seperti rate limiting
    dan proteksi CSRF, serta menggunakan database in-memory untuk isolasi tes.
    """
    RATELIMIT_ENABLED = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Konfigurasi untuk lingkungan produksi.

    Memastikan SECRET_KEY tersedia dan menonaktifkan mode debug serta testing
    untuk mengutamakan keamanan, stabilitas, dan performa sistem.
    """
    if not Config.SECRET_KEY:
        raise ValueError('SECRET_KEY tidak ditemukan. Harap atur environment variable.')
    
    DEBUG = False
    TESTING = False

class SecurityTestingConfig(DevelopmentConfig):
    """Konfigurasi untuk pengujian keamanan (misal: SQLMap).
    
    Menggunakan database pengembangan tetapi menonaktifkan beberapa fitur keamanan
    seperti rate limiting dan proteksi CSRF untuk memfasilitasi pengujian penetrasi.
    """
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False
    SESSION_PROTECTION = 'basic'

# Dictionary untuk mengakses kelas konfigurasi berdasarkan nama string
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'security': SecurityTestingConfig,
    'default': DevelopmentConfig
}