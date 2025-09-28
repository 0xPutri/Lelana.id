import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Kelas konfigurasi dasar yang berlaku untuk semua lingkungan di Lelana.id.

    Menyediakan pengaturan default untuk keamanan, database, unggahan file,
    dan batasan konten. Nilai diutamakan dari variabel lingkungan (.env),
    dengan fallback ke nilai default yang aman untuk pengembangan lokal.

    Atribut:
        SECRET_KEY (str): Kunci rahasia aplikasi (wajib di produksi, dari .env).
        SQLALCHEMY_DATABASE_URI (str): URI database (default: SQLite lelana.db).
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Dinonaktifkan untuk efisiensi.
        UPLOAD_FOLDER (str): Direktori penyimpanan file unggahan pengguna.
        ALLOWED_EXTENSIONS (set): Ekstensi gambar yang diizinkan (png, jpg, jpeg, gif).
        MAX_CONTENT_LENGTH (int): Batas ukuran unggahan maksimal (10 MB).
    """
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lelana.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

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

    Digunakan saat Lelana.id di-deploy ke server publik. Semua fitur debugging
    dan pengujian dinonaktifkan demi keamanan dan stabilitas. Aplikasi akan
    memastikan bahwa SECRET_KEY telah diatur melalui variabel lingkungan;
    jika tidak, sistem akan gagal startup dengan pesan error eksplisit untuk
    mencegah deployment dengan konfigurasi tidak aman.

    Atribut:
        DEBUG (bool): False — mencegah kebocoran informasi internal.
        TESTING (bool): False — nonaktif karena tidak relevan di produksi.

    Raises:
        ValueError: Jika SECRET_KEY tidak ditemukan di variabel lingkungan,
                    menghentikan inisialisasi aplikasi untuk mencegah risiko keamanan.
    """
    if not Config.SECRET_KEY:
        raise ValueError('SECRET_KEY tidak ditemukan. Harap atur environment variable.')
    
    DEBUG = False
    TESTING = False

# Dictionary untuk mengakses kelas konfigurasi berdasarkan nama
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}