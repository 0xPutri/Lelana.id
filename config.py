import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Kelas dasar konfigurasi aplikasi dengan pengaturan umum.

    Mengelola variabel lingkungan, konfigurasi database, keamanan,
    unggah file, dan pengaturan email. Dirancang untuk diwariskan
    oleh kelas konfigurasi spesifik lingkungan (development, testing, production).

    Attributes:
        SECRET_KEY (str): Kunci rahasia untuk sesi dan keamanan CSRF.
        SQLALCHEMY_DATABASE_URI (str): URI koneksi database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Nonaktifkan pelacakan modifikasi SQLAlchemy.
        UPLOAD_FOLDER (str): Direktori penyimpanan file yang diunggah.
        ALLOWED_EXTENSIONS (set): Ekstensi file yang diizinkan untuk diunggah.
        MAX_CONTENT_LENGTH (int): Batas ukuran unggahan (10 MB).
        MAIL_SERVER (str): Server SMTP untuk pengiriman email.
        MAIL_PORT (int): Port server email.
        MAIL_USE_TLS (bool): Aktifkan TLS untuk koneksi email.
        MAIL_USE_SSL (bool): Aktifkan SSL untuk koneksi email.
        MAIL_USERNAME (str): Username autentikasi email.
        MAIL_PASSWORD (str): Password autentikasi email.
        MAIL_SENDER (tuple): Identitas pengirim email default.
        BAD_WORDS_ID (list): Daftar kata terlarang untuk filtering konten.
        ALLOWED_EMAIL_DOMAINS (list): Domain email yang diizinkan. 
        GEMINI_API_KEY (str): Kunci API untuk mengakses layanan Gemini (Google Generative AI).
        SERPER_API_KEY (str): Kunci API untuk mengakses layanan Serper (Search API).
    """
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

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lelana.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = ('Tim Lelana.id', os.environ.get('MAIL_USERNAME'))

    _bad_words_str = os.environ.get('BAD_WORDS_ID', '')
    BAD_WORDS_ID = [word.strip() for word in _bad_words_str.split(',') if word.strip()]

    _allowed_domains_str = os.environ.get('ALLOWED_EMAIL_DOMAINS', 'gmail.com,hotmail.com,outlook.com,yahoo.com,ymail.com,live.com,icloud.com,me.com,mac.com,aol.com,protonmail.com,tutanota.com,zoho.com,gmx.com,mail.com,yandex.com,fastmail.com,hey.com,duck.com,inbox.com,hushmail.com,msn.com,qq.com,163.com,126.com,pm.me,proton.me,lelana.my.id')
    ALLOWED_EMAIL_DOMAINS = [domain.strip() for domain in _allowed_domains_str.split(',') if domain.strip()]

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY')

class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan pengembangan.

    Mengaktifkan mode debug untuk memudahkan pengembangan lokal.
    """
    DEBUG = True

class TestingConfig(Config):
    """Konfigurasi untuk lingkungan pengujian otomatis.

    Menonaktifkan rate limiting dan CSRF protection untuk memudahkan pengujian,
    serta menggunakan database in-memory SQLite.
    """
    RATELIMIT_ENABLED = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False # Nonaktifkan CSRF saat menjalankan tes

class ProductionConfig(Config):
    """Konfigurasi untuk lingkungan produksi.

    Memastikan SECRET_KEY tersedia dan menonaktifkan mode debug serta testing.
    Mengutamakan keamanan dan stabilitas sistem.
    """
    if not Config.SECRET_KEY:
        raise ValueError('SECRET_KEY tidak ditemukan. Harap atur environment variable.')
    
    DEBUG = False
    TESTING = False

class SecurityTestingConfig(DevelopmentConfig):
    """Konfigurasi untuk pengujian keamanan (misal: SQLMap).
    
    Menggunakan database pengembangan tetapi menonaktifkan rate limiting, proteksi CSRF,
    dan mengurangi proteksi sesi.
    """
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False
    SESSION_PROTECTION = 'basic'

# Dictionary untuk mengakses kelas konfigurasi berdasarkan nama
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'security': SecurityTestingConfig,
    'default': DevelopmentConfig
}