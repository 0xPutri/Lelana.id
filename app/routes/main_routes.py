from flask import Blueprint, render_template
from flask_login import login_required, current_user

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

    Hanya tersedia untuk pengguna terautentikasi. Menampilkan informasi akun
    dasar seperti username, email, dan peran, serta akses ke riwayat ulasan
    dan itinerari pribadi (jika dikembangkan lebih lanjut).

    Returns:
        Response: Render template 'main/profile.html' dengan objek current_user.
    """
    return render_template('main/profile.html', user=current_user)

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