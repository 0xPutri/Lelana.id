from flask import Blueprint, render_template

# Membuat Blueprint untuk menangani halaman error kustom
errors = Blueprint('errors', __name__)

@errors.app_errorhandler(401)
def unauthorized(e):
    """Menangani error HTTP 401 Unauthorized.

    Handler ini dipicu ketika pengguna mencoba mengakses sumber daya yang
    memerlukan autentikasi tetapi belum login.

    Args:
        e (Exception): Instance error yang ditangkap oleh Flask.

    Returns:
        tuple[Response, int]: Template error 401 dan kode status HTTP 401.
    """
    # Merender halaman kustom untuk error 401
    return render_template('errors/401.html'), 401

@errors.app_errorhandler(403)
def forbidden(e):
    """Menangani error HTTP 403 Forbidden.

    Handler ini dipicu ketika pengguna yang sudah terautentikasi mencoba
    mengakses sumber daya yang tidak diizinkan untuk perannya.

    Args:
        e (Exception): Instance error yang ditangkap oleh Flask.

    Returns:
        tuple[Response, int]: Template error 403 dan kode status HTTP 403.
    """
    # Merender halaman kustom untuk error 403
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(404)
def page_not_found(e):
    """Menangani error HTTP 404 Not Found.

    Handler ini dipicu ketika rute atau sumber daya yang diminta tidak
    dapat ditemukan di server.

    Args:
        e (Exception): Instance error yang ditangkap oleh Flask.

    Returns:
        tuple[Response, int]: Template error 404 dan kode status HTTP 404.
    """
    # Merender halaman kustom untuk error 404
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(429)
def too_many_requests(e):
    """Menangani error HTTP 429 Too Many Requests.

    Handler ini dipicu oleh ekstensi Flask-Limiter ketika pengguna
    melebihi batas permintaan yang telah ditentukan.

    Args:
        e (Exception): Instance error yang ditangkap oleh Flask.

    Returns:
        tuple[Response, int]: Template error 429 dan kode status HTTP 429.
    """
    # Merender halaman kustom untuk error 429
    return render_template('errors/429.html'), 429

@errors.app_errorhandler(500)
def internal_server_error(e):
    """Menangani error HTTP 500 Internal Server Error.

    Handler ini dipicu ketika terjadi kesalahan tak terduga di sisi server
    saat memproses permintaan.

    Args:
        e (Exception): Instance error yang ditangkap oleh Flask.

    Returns:
        tuple[Response, int]: Template error 500 dan kode status HTTP 500.
    """
    # Merender halaman kustom untuk error 500
    return render_template('errors/500.html'), 500
