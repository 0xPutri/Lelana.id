from flask import Flask
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

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
mail = Mail()
csrf = CSRFProtect()

def create_app(config_name):
    """Membuat dan mengonfigurasi instance aplikasi Flask berdasarkan nama konfigurasi.

    Fungsi ini menginisialisasi semua ekstensi inti (database, login, rate limiting,
    email, CSRF protection), memuat filter konten, mendaftarkan blueprint rute,
    dan mengatur optimasi khusus untuk database SQLite (mode WAL dan timeout).
    Menggunakan factory pattern untuk mendukung berbagai lingkungan.

    Args:
        config_name (str): Nama konfigurasi yang sesuai dengan kunci di modul `config`.

    Returns:
        Flask: Instance aplikasi Flask yang telah dikonfigurasi dan siap dijalankan.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from .utils.text_filters import init_profanity_filter
    init_profanity_filter(app)

    db.init_app(app)
    login_manager.init_app(app)

    limiter.init_app(app)

    mail.init_app(app)
    csrf.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    register_blueprints(app)

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite') and ':memory:' not in db_uri:
        with app.app_context():
            engine = db.get_engine()
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                try:
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA busy_timeout = 5000")
                finally:
                    cursor.close()

    return app

def register_blueprints(app):
    """Mendaftarkan semua blueprint rute ke aplikasi Flask secara terpusat.

    Menghindari duplikasi kode pendaftaran blueprint dengan menggunakan daftar
    terstruktur yang berisi nama modul, nama objek blueprint, dan prefix URL.

    Args:
        app (Flask): Instance aplikasi Flask tempat blueprint akan didaftarkan.
    """
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

    for module_name, bp_name, prefix in blueprints:
        module = import_module(f'.routes.{module_name}', package=__package__)
        blueprint = getattr(module, bp_name)

        app.register_blueprint(blueprint, url_prefix=prefix)