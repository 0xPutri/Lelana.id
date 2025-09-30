from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.itinerari import Itinerari
from app.models.wisata import Wisata
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app import db
from sqlalchemy.orm import joinedload
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Menampilkan halaman utama (landing page) Lelana.id dengan konten dinamis unggulan.

    Memuat empat jenis konten utama:
    - 3 destinasi wisata terpopuler berdasarkan jumlah ulasan dan rata-rata rating,
    - 3 event budaya mendatang (tanggal ≥ hari ini), diurutkan dari yang paling dekat,
    - 3 itinerari perjalanan terbaru dari komunitas pengguna,
    - Semua paket wisata yang ditandai sebagai promosi (`is_promoted=True`).

    Query destinasi menggunakan agregasi (COUNT, AVG) dan outer join untuk
    menampilkan peringkat berdasarkan partisipasi pengguna. Halaman ini bersifat
    publik dan menjadi pintu masuk utama bagi pengunjung baru untuk menjelajahi
    kekayaan wisata dan budaya Banyumas melalui Lelana.id.

    Returns:
        Response: Render template 'main/index.html' dengan data konten unggulan.
    """
    destinasi_unggulan = db.session.query(
        Wisata,
        db.func.count(Review.id).label('jumlah_review'),
        db.func.avg(Review.rating).label('rata_rata_rating')
    ).outerjoin(Review, Wisata.id == Review.wisata_id)\
    .group_by(Wisata.id)\
    .order_by(db.desc('jumlah_review'), db.desc('rata_rata_rating'))\
    .limit(3).all()

    event_terbaru = Event.query.filter(Event.tanggal >= datetime.utcnow()).order_by(Event.tanggal.asc()).limit(3).all()

    itinerari_terbaru = Itinerari.query.order_by(Itinerari.tanggal_dibuat.desc()).limit(3).all()

    paket_promosi = PaketWisata.query.filter_by(is_promoted=True).all()

    return render_template('main/index.html', 
                           destinasi_list=destinasi_unggulan, 
                           event_list=event_terbaru, 
                           itinerari_list=itinerari_terbaru, 
                           paket_promosi_list=paket_promosi)

@main.route('/profile')
@login_required
def profile():
    """
    Menampilkan halaman profil pribadi pengguna yang sedang login.

    Memuat data aktivitas pengguna secara lengkap, meliputi:
    - Daftar ulasan yang pernah dibuat, dilengkapi informasi destinasi terkait
      (dimuat secara eager menggunakan joinedload untuk efisiensi query),
    - Daftar itinerari perjalanan yang dibuat, diurutkan dari yang terbaru.

    Hanya dapat diakses oleh pengguna terautentikasi. Halaman ini menjadi pusat
    manajemen identitas dan kontribusi pengguna di ekosistem Lelana.id.

    Returns:
        Response: Render template 'main/profile.html' dengan data pengguna dan aktivitasnya.
    """
    ulasan_pengguna = Review.query.filter_by(user_id=current_user.id)\
        .options(joinedload(Review.wisata_reviewed))\
        .order_by(Review.tanggal_dibuat.desc())\
        .all()
    
    itinerari_pengguna = Itinerari.query.filter_by(user_id=current_user.id)\
        .order_by(Itinerari.tanggal_dibuat.desc())\
        .all()

    return render_template('main/profile.html', 
                           user=current_user, 
                           ulasan_list=ulasan_pengguna, 
                           itinerari_list=itinerari_pengguna)

@main.route('/peta-wisata')
def peta_wisata():
    """
    Menampilkan halaman peta interaktif destinasi wisata di Banyumas.

    Mengintegrasikan data lokasi (latitude/longitude) dari model Wisata untuk
    menampilkan marker pada peta berbasis web (misalnya Leaflet atau Google Maps).
    Dapat diakses secara publik sebagai fitur eksplorasi destinasi.

    Returns:
        Response: Render template 'main/peta.html'.
    """
    return render_template('main/peta.html')