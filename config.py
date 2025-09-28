import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Kelas konfigurasi dasar yang berlaku untuk semua lingkungan pada Lelana.id.

    Menyediakan pengaturan default untuk keamanan, database, dan manajemen file
    unggahan. Nilai konfigurasi diutamakan dari variabel lingkungan (.env),
    dengan fallback ke nilai default yang sesuai untuk pengembangan lokal.

    Atribut:
        SECRET_KEY (str): Kunci rahasia aplikasi (dari .env atau default).
        SQLALCHEMY_DATABASE_URI (str): URI database (default: SQLite lelana.db).
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Dinonaktifkan untuk efisiensi.
        UPLOAD_FOLDER (str): Direktori penyimpanan file unggahan.
        ALLOWED_EXTENSIONS (set): Ekstensi gambar yang diizinkan (png, jpg, dll).
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or '$^peg=i8qm@*!-a2ew!l)kf@#ix@djujv**#-o%sqga!x%8hsj'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lelana.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """
    Konfigurasi khusus untuk lingkungan pengembangan (development).

    Digunakan selama fase implementasi fitur dan debugging lokal. Mode DEBUG
    diaktifkan untuk menampilkan pesan kesalahan mendetail dan mempercepat
    iterasi pengembangan.

    Atribut:
        DEBUG (bool): Diatur ke True untuk mengaktifkan mode debug Flask.
    """
    DEBUG = True

class TestingConfig(Config):
    """
    Konfigurasi khusus untuk lingkungan pengujian (testing).

    Menggunakan database terpisah dan menonaktifkan fitur yang menghambat
    otomatisasi pengujian, seperti proteksi CSRF, agar skenario uji fungsional
    dan integrasi dapat dijalankan secara lancar.

    Atribut:
        TESTING (bool): Aktifkan mode pengujian Flask.
        SQLALCHEMY_DATABASE_URI (str): Database SQLite khusus untuk pengujian.
        WTF_CSRF_ENABLED (bool): Dinonaktifkan agar form dapat diuji tanpa token CSRF.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_lelana.db')
    WTF_CSRF_ENABLED = False # Nonaktifkan CSRF saat menjalankan tes

class ProductionConfig(Config):
    """
    Konfigurasi untuk lingkungan produksi (production).

    Digunakan saat aplikasi Lelana.id di-deploy ke server publik. Semua fitur
    debugging dan pengujian dinonaktifkan untuk menjaga keamanan dan stabilitas
    sistem. Di lingkungan nyata, nilai seperti SECRET_KEY dan DATABASE_URL
    harus diatur melalui variabel lingkungan yang aman.

    Atribut:
        DEBUG (bool): Dinonaktifkan (False) untuk mencegah kebocoran informasi.
        TESTING (bool): Dinonaktifkan (False) karena tidak relevan di produksi.
    """
    DEBUG = False
    TESTING = False

# Dictionary untuk mengakses kelas konfigurasi berdasarkan nama
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}