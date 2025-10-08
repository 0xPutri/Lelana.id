from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.itinerari import Itinerari
from app.models.wisata import Wisata
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app import db
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Menampilkan halaman utama situs dengan konten unggulan.

    Menyajikan:
    - 3 destinasi wisata terpopuler berdasarkan jumlah ulasan dan rating rata-rata,
    - 3 acara mendatang yang diurutkan berdasarkan tanggal terdekat,
    - 3 itinerari terbaru yang dibuat pengguna,
    - Semua paket wisata yang ditandai sebagai promosi.

    Returns:
        Response: Render template halaman utama dengan data konten unggulan.
    """
    destinasi_unggulan = db.session.query(
        Wisata,
        db.func.count(Review.id).label('jumlah_review'),
        db.func.avg(Review.rating).label('rata_rata_rating')
    ).outerjoin(Review, Wisata.id == Review.wisata_id)\
    .group_by(Wisata.id)\
    .order_by(db.desc('jumlah_review'), db.desc('rata_rata_rating'))\
    .limit(3).all()

    event_terbaru = Event.query.filter(Event.tanggal >= datetime.now(timezone.utc)).order_by(Event.tanggal.asc()).limit(3).all()

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
    """Menampilkan halaman profil pengguna yang sedang login.

    Memuat daftar ulasan dan itinerari yang dibuat oleh pengguna saat ini,
    diurutkan berdasarkan waktu pembuatan (terbaru di atas). Ulasan mencakup
    informasi tempat wisata yang diulas melalui eager loading.

    Returns:
        Response: Render template profil pengguna dengan data ulasan dan itinerari.
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
    """Menampilkan halaman peta interaktif tempat wisata.

    Template ini diharapkan menampilkan lokasi wisata berbasis koordinat geografis.

    Returns:
        Response: Render template peta wisata.
    """
    return render_template('main/peta.html')

@main.route('/about')
def about():
    """Menampilkan halaman 'Tentang Kami' yang menjelaskan misi dan visi platform.

    Returns:
        Response: Render template halaman tentang kami.
    """
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    """Menampilkan halaman kontak dengan informasi cara menghubungi tim Lelana.id.

    Returns:
        Response: Render template halaman kontak.
    """
    return render_template('main/contact.html')

@main.route('/privacy')
def privacy():
    """Menampilkan kebijakan privasi platform Lelana.id.

    Returns:
        Response: Render template halaman kebijakan privasi.
    """
    return render_template('main/privacy.html')