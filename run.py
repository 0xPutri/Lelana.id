import os
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env jika ada
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Impor factory function dan objek database setelah konfigurasi dimuat
from app import create_app, db
from app.models.user import User
from app.models.wisata import Wisata
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app.models.itinerari import Itinerari
from app.models.review import Review
from app.models.foto_ulasan import FotoUlasan
from flask_migrate import Migrate

# Membuat instance aplikasi menggunakan konfigurasi dari environment variable atau default
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# Menginisialisasi Flask-Migrate untuk manajemen migrasi database
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Menyediakan konteks variabel untuk sesi shell Flask.

    Fungsi ini secara otomatis mengimpor instance database dan model-model utama
    ke dalam shell Flask, memudahkan debugging dan interaksi manual.

    Returns:
        dict: Dictionary berisi objek-objek yang akan tersedia di shell.
    """
    return dict(
        db=db, User=User, Wisata=Wisata, Event=Event, PaketWisata=PaketWisata,
        Itinerari=Itinerari, Review=Review, FotoUlasan=FotoUlasan
    )

if __name__ == '__main__':
    app.run()
