from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name):
    """
    Membuat dan mengonfigurasi instance aplikasi Flask untuk Lelana.id
    menggunakan pola Application Factory.

    Fungsi ini bertanggung jawab atas inisialisasi inti aplikasi, termasuk:
    - Pemuatan konfigurasi berdasarkan lingkungan (development/testing/production),
    - Pemasangan ekstensi: database (SQLAlchemy), autentikasi (Flask-Login),
      dan pembatasan laju permintaan (Flask-Limiter),
    - Pendaftaran blueprint untuk modularisasi rute,
    - Penanganan muatan pengguna terautentikasi.

    Fitur keamanan tambahan:
    - Session protection diatur ke 'strong' untuk mencegah pencurian sesi.
    - Rate limiting diterapkan secara global: maksimal 200 permintaan per hari
      dan 50 permintaan per jam per alamat IP, guna mencegah penyalahgunaan
      (misalnya brute-force pada rute login).

    Pendekatan ini mendukung pengujian terisolasi, deployment fleksibel,
    dan pemeliharaan kode yang bersih — sesuai prinsip mata kuliah
    Implementasi dan Pengujian Perangkat Lunak.

    Args:
        config_name (str): Nama lingkungan konfigurasi ('development', 'testing',
                           'production', atau 'default').

    Returns:
        Flask: Instance aplikasi Flask yang telah dikonfigurasi dan siap dijalankan.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    # Menghubungkan limiter dengan instance aplikasi
    limiter.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.main_routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.auth_routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .routes.wisata_routes import wisata as wisata_blueprint
    app.register_blueprint(wisata_blueprint)

    from .routes.event_routes import event as event_blueprint
    app.register_blueprint(event_blueprint)

    from .routes.paket_wisata_routes import paket_wisata as paket_wisata_blueprint
    app.register_blueprint(paket_wisata_blueprint)

    from .routes.itinerari_routes import itinerari as itinerari_blueprint
    app.register_blueprint(itinerari_blueprint)

    from .routes.admin_routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .routes.error_routes import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    return app