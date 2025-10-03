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
    """Menyediakan konteks variabel yang tersedia saat menggunakan Flask shell.

    Fungsi ini secara otomatis memuat instance database dan model-model utama
    ke dalam lingkungan shell Flask, sehingga pengembang dapat mengaksesnya
    secara langsung tanpa perlu mengimpor ulang.

    Returns:
        dict: Dictionary berisi objek-objek yang akan tersedia di Flask shell,
              termasuk `db`, `User`, `Wisata`, `Event`, `PaketWisata`,
              `Itinerari`, `Review`, dan `FotoUlasan`.
    """
    return dict(
        db=db, User=User, Wisata=Wisata, Event=Event, PaketWisata=PaketWisata,
        Itinerari=Itinerari, Review=Review, FotoUlasan=FotoUlasan
    )