from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(401)
def unauthorized(e):
    """Menangani error HTTP 401 Unauthorized.

    Ditampilkan ketika pengguna mencoba mengakses sumber daya yang memerlukan
    autentikasi tanpa login.

    Args:
        e (Exception): Instance error yang ditangkap.

    Returns:
        tuple: Template error 401 dan kode status HTTP 401.
    """
    return render_template('errors/401.html'), 401

@errors.app_errorhandler(403)
def forbidden(e):
    """Menangani error HTTP 403 Forbidden.

    Ditampilkan ketika pengguna tidak memiliki izin untuk mengakses sumber daya,
    meskipun sudah login (misalnya, pengguna biasa mengakses halaman admin).

    Args:
        e (Exception): Instance error yang ditangkap.

    Returns:
        tuple: Template error 403 dan kode status HTTP 403.
    """
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(404)
def page_not_found(e):
    """Menangani error HTTP 404 Not Found.

    Ditampilkan ketika rute atau sumber daya yang diminta tidak ditemukan.

    Args:
        e (Exception): Instance error yang ditangkap.

    Returns:
        tuple: Template error 404 dan kode status HTTP 404.
    """
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(429)
def too_many_requests(e):
    """Menangani error HTTP 429 Too Many Requests.

    Ditampilkan ketika pengguna melebihi batas permintaan yang diizinkan
    (rate limiting), misalnya terlalu banyak percobaan login.

    Args:
        e (Exception): Instance error yang ditangkap.

    Returns:
        tuple: Template error 429 dan kode status HTTP 429.
    """
    return render_template('errors/429.html'), 429

@errors.app_errorhandler(500)
def internal_server_error(e):
    """Menangani error HTTP 500 Internal Server Error.

    Ditampilkan ketika terjadi kesalahan tak terduga di sisi server.

    Args:
        e (Exception): Instance error yang ditangkap.

    Returns:
        tuple: Template error 500 dan kode status HTTP 500.
    """
    return render_template('errors/500.html'), 500