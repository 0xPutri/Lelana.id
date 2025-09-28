from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.review import Review
from app.models.itinerari import Itinerari

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Menampilkan halaman utama (landing page) Lelana.id.

    Berisi pengantar platform, daftar destinasi unggulan, event terbaru,
    dan navigasi utama. Dapat diakses oleh semua pengunjung (publik).

    Returns:
        Response: Render template 'main/index.html'.
    """
    return render_template('main/index.html')

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