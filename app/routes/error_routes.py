from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(401)
def unauthorized(e):
    """
    Menangani respons HTTP 401 Unauthorized.

    Ditampilkan ketika pengguna mencoba mengakses sumber daya yang memerlukan
    autentikasi tanpa login terlebih dahulu (misalnya mengakses dashboard
    pengguna secara langsung tanpa sesi aktif).

    Args:
        e (Exception): Objek exception yang dilempar oleh Flask.

    Returns:
        tuple: Template HTML 'errors/401.html' dan kode status HTTP 401.
    """
    return render_template('errors/401.html'), 401

@errors.app_errorhandler(403)
def forbidden(e):
    """
    Menangani respons HTTP 403 Forbidden.

    Muncul ketika pengguna terautentikasi mencoba mengakses fitur yang tidak
    diizinkan berdasarkan perannya (misalnya pengguna biasa mengakses rute admin
    yang dilindungi oleh dekorator @admin_required).

    Args:
        e (Exception): Objek exception yang dilempar oleh Flask.

    Returns:
        tuple: Template HTML 'errors/403.html' dan kode status HTTP 403.
    """
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(404)
def page_not_found(e):
    """
    Menangani respons HTTP 404 Not Found.

    Ditampilkan ketika pengguna mengakses URL yang tidak terdaftar di aplikasi,
    baik karena salah ketik, tautan rusak, atau rute yang telah dihapus.

    Args:
        e (Exception): Objek exception yang dilempar oleh Flask.

    Returns:
        tuple: Template HTML 'errors/404.html' dan kode status HTTP 404.
    """
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(500)
def internal_server_error(e):
    """
    Menangani respons HTTP 500 Internal Server Error.

    Digunakan untuk menangkap kesalahan tak terduga di sisi server (misalnya
    exception tidak tertangani, kegagalan query database, atau kesalahan logika).
    Template ini memberikan pengalaman pengguna yang lebih ramah daripada
    menampilkan traceback mentah.

    Args:
        e (Exception): Objek exception internal yang terjadi selama permintaan.

    Returns:
        tuple: Template HTML 'errors/500.html' dan kode status HTTP 500.
    """
    return render_template('errors/500.html'), 500