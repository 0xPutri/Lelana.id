from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    """
    Membuat dan mengonfigurasi instance aplikasi Flask untuk Lelana.id
    menggunakan pola Application Factory.

    Fungsi ini bertanggung jawab atas inisialisasi inti aplikasi, termasuk:
    - Pemuatan konfigurasi berdasarkan nama lingkungan (development/testing/production),
    - Pemasangan ekstensi (database, autentikasi),
    - Pendaftaran blueprint untuk modularisasi rute,
    - Penanganan muatan pengguna terautentikasi.

    Pendekatan ini memungkinkan pengujian unit yang terisolasi dan deployment
    fleksibel di berbagai lingkungan, sesuai prinsip pengembangan perangkat lunak
    yang baik dalam mata kuliah Implementasi dan Pengujian Perangkat Lunak.

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

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
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