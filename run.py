import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, db
from app.models.user import User
from app.models.wisata import Wisata
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app.models.itinerari import Itinerari
from app.models.review import Review
from app.models.foto_ulasan import FotoUlasan
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """
    Menyediakan konteks shell interaktif Flask dengan objek-objek inti aplikasi
    untuk keperluan debugging, pengujian manual, dan eksplorasi data selama
    pengembangan.

    Fungsi ini secara otomatis memuat instance database dan model-model utama
    Lelana.id ke dalam lingkungan Flask shell, sehingga developer dapat
    langsung berinteraksi dengan model seperti User, Wisata, Review, dll.
    tanpa perlu mengimpor ulang secara manual.

    Digunakan terutama selama fase implementasi dan pengujian perangkat lunak
    untuk memverifikasi struktur data, operasi CRUD, serta relasi antar entitas
    dalam database SQLite.

    Returns:
        dict: Kamus berisi pasangan nama-objek yang akan tersedia di Flask shell,
              mencakup:
              - 'db': instance SQLAlchemy untuk operasi database,
              - Model-model domain: User, Wisata, Event, PaketWisata,
                Itinerari, Review, dan FotoUlasan.
    """
    return dict(
        db=db, User=User, Wisata=Wisata, Event=Event, PaketWisata=PaketWisata,
        Itinerari=Itinerari, Review=Review, FotoUlasan=FotoUlasan
    )