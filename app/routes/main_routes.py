from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.itinerari import Itinerari
from app.models.wisata import Wisata
from app.models.event import Event
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Menampilkan halaman utama (landing page) Lelana.id dengan konten dinamis.

    Menyajikan tiga jenis konten utama:
    1. 3 destinasi unggulan: dipilih berdasarkan jumlah ulasan terbanyak, lalu
        diurutkan berdasarkan rata-rata rating tertinggi (menggunakan
        LEFT JOIN agar destinasi tanpa ulasan tetap muncul).
    2. 3 event mendatang: acara budaya yang tanggal pelaksanaannya
        belum lewat, diurutkan dari yang paling dekat.
    3. 3 itinerari terbaru: rencana perjalanan yang baru saja dibuat pengguna.

    Halaman ini dirancang sebagai pintu masuk utama bagi pengunjung umum,
    memberikan gambaran hidup tentang aktivitas dan konten terkini di platform.

    Returns:
        Response: Render template 'main/index.html' dengan daftar destinasi,
                  event, dan itinerari untuk ditampilkan di beranda.
    """
    destinasi_unggulan = db.session.query(
        Wisata,
        db.func.count(Review.id).label('jumlah_review'),
        db.func.avg(Review.rating).label('rata_rata_rating')
    ).outerjoin(Review, Wisata.id == Review.wisata_id)\
    .group_by(Wisata.id)\
    .order_by(db.desc('jumlah_review'), db.desc('rata_rata_rating'))\
    .limit(3).all()

    from datetime import datetime
    event_terbaru = Event.query.filter(Event.tanggal >= datetime.utcnow()).order_by(Event.tanggal.asc()).limit(3).all()

    itinerari_terbaru = Itinerari.query.order_by(Itinerari.tanggal_dibuat.desc()).limit(3).all()

    return render_template('main/index.html', 
                           destinasi_list=destinasi_unggulan, 
                           event_list=event_terbaru, 
                           itinerari_list=itinerari_terbaru)

@main.route('/profile')
@login_required
def profile():
    """
    Menampilkan halaman profil pribadi pengguna yang sedang login.

    Menyertakan informasi akun dasar serta dua daftar konten yang dibuat pengguna:
    - Ulasan destinasi wisata, diurutkan dari yang terbaru.
    - Itinerari perjalanan, diurutkan dari yang terbaru.

    Hanya dapat diakses oleh pengguna terautentikasi. Data disusun untuk
    memberikan gambaran lengkap tentang kontribusi pengguna di platform Lelana.id.

    Returns:
        Response: Render template 'main/profile.html' dengan data pengguna,
        daftar ulasan, dan daftar itinerari.
    """
    ulasan_pengguna = current_user.reviews.order_by(Review.tanggal_dibuat.desc()).all()

    itinerari_pengguna = current_user.itinerari.order_by(Itinerari.tanggal_dibuat.desc()).all()

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