from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.itinerari import Itinerari
from app.models.wisata import Wisata
from app.models.event import Event
from app.models.paket_wisata import PaketWisata
from app import db
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

# Membuat Blueprint untuk rute-rute utama dan halaman statis
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Menampilkan halaman utama (beranda) dengan konten dinamis.

    Halaman ini menampilkan beberapa bagian konten unggulan seperti destinasi
    populer, event terbaru, itinerari terbaru, dan paket promosi.

    Returns:
        Response: Render template halaman utama dengan data yang relevan.
    """
    # Query untuk mendapatkan 3 destinasi terpopuler
    # Popularitas dihitung berdasarkan jumlah review dan rating rata-rata
    destinasi_unggulan = db.session.query(
        Wisata,
        db.func.count(Review.id).label('jumlah_review'),
        db.func.avg(Review.rating).label('rata_rata_rating')
    ).outerjoin(Review, Wisata.id == Review.wisata_id)\
    .group_by(Wisata.id)\
    .order_by(db.desc('jumlah_review'), db.desc('rata_rata_rating'))\
    .limit(3).all()

    # Query untuk mendapatkan 3 event mendatang (tanggal lebih besar atau sama dengan hari ini)
    event_terbaru = Event.query.filter(Event.tanggal >= datetime.now(timezone.utc)).order_by(Event.tanggal.asc()).limit(3).all()

    # Query untuk mendapatkan 3 itinerari terbaru
    itinerari_terbaru = Itinerari.query.order_by(Itinerari.tanggal_dibuat.desc()).limit(3).all()

    # Query untuk mendapatkan semua paket wisata yang sedang dipromosikan
    paket_promosi = PaketWisata.query.filter_by(is_promoted=True).all()

    return render_template('main/index.html', 
                           destinasi_list=destinasi_unggulan, 
                           event_list=event_terbaru, 
                           itinerari_list=itinerari_terbaru, 
                           paket_promosi_list=paket_promosi)

@main.route('/profile')
@login_required
def profile():
    """Menampilkan halaman profil untuk pengguna yang sedang login.

    Menampilkan daftar ulasan dan itinerari yang telah dibuat oleh pengguna.

    Returns:
        Response: Render template halaman profil dengan data milik pengguna.
    """
    # Mengambil semua ulasan milik pengguna, diurutkan dari yang terbaru
    # joinedload(Review.wisata_reviewed) untuk efisiensi query data wisata terkait
    ulasan_pengguna = Review.query.filter_by(user_id=current_user.id)\
        .options(joinedload(Review.wisata_reviewed))\
        .order_by(Review.tanggal_dibuat.desc())\
        .all()
    
    # Mengambil semua itinerari milik pengguna, diurutkan dari yang terbaru
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

    Returns:
        Response: Render template halaman peta.
    """
    return render_template('main/peta.html')

@main.route('/about')
def about():
    """Menampilkan halaman statis 'Tentang Kami'.

    Returns:
        Response: Render template halaman 'about'.
    """
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    """Menampilkan halaman statis 'Kontak'.

    Returns:
        Response: Render template halaman 'contact'.
    """
    return render_template('main/contact.html')

@main.route('/privacy')
def privacy():
    """Menampilkan halaman statis 'Kebijakan Privasi'.

    Returns:
        Response: Render template halaman 'privacy'.
    """
    return render_template('main/privacy.html')

@main.route('/search')
def search():
    """Menangani pencarian di seluruh situs berdasarkan query pengguna.

    Mencari kata kunci pada beberapa model (Wisata, Event, PaketWisata,
    Itinerari) di kolom-kolom yang relevan secara case-insensitive.

    Returns:
        Response: Render template halaman hasil pencarian dengan semua
                  hasil yang ditemukan.
    """
    # Mengambil query pencarian dari argumen URL
    query = request.args.get('q', '')
    wisata_results = []
    event_results = []
    paket_wisata_results = []
    itinerari_results = []

    # Hanya menjalankan query jika ada kata kunci pencarian
    if query:
        # Menyiapkan term pencarian untuk query 'LIKE' yang case-insensitive
        search_term = f"%{query}%"
        
        # Mencari di model Wisata pada kolom nama, deskripsi, dan lokasi
        wisata_results = Wisata.query.filter(
            or_(
                Wisata.nama.ilike(search_term),
                Wisata.deskripsi.ilike(search_term),
                Wisata.lokasi.ilike(search_term)
            )
        ).all()

        # Mencari di model Event pada kolom nama dan deskripsi
        event_results = Event.query.filter(
            or_(
                Event.nama.ilike(search_term),
                Event.deskripsi.ilike(search_term)
            )
        ).all()

        # Mencari di model PaketWisata pada kolom nama dan deskripsi
        paket_wisata_results = PaketWisata.query.filter(
            or_(
                PaketWisata.nama.ilike(search_term),
                PaketWisata.deskripsi.ilike(search_term)
            )
        ).all()
        
        # Mencari di model Itinerari pada kolom judul dan deskripsi
        itinerari_results = Itinerari.query.filter(
            or_(
                Itinerari.judul.ilike(search_term),
                Itinerari.deskripsi.ilike(search_term)
            )
        ).all()

    return render_template('main/search_results.html',
                           query=query,
                           wisata_list=wisata_results,
                           event_list=event_results,
                           paket_wisata_list=paket_wisata_results,
                           itinerari_list=itinerari_results)
