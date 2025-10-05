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

    Fungsi ini menginisialisasi ekstensi inti (database, login, rate limiting, email),
    memuat filter teks, mendaftarkan blueprint rute, dan mengatur loader pengguna.
    Untuk database SQLite berbasis file (bukan in-memory), mengaktifkan mode WAL
    dan mengatur busy timeout untuk meningkatkan konkurensi dan stabilitas.

    Args:
        config_name (str): Nama konfigurasi yang sesuai dengan kunci di modul `config`
                           (misalnya 'default', 'development', 'production').

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

    from .routes.chatbot_routes import chatbot as chatbot_blueprint
    app.register_blueprint(chatbot_blueprint)

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