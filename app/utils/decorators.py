from functools import wraps
from flask_login import current_user
from flask import abort

def admin_required(f):
    """
    Dekorator untuk membatasi akses rute hanya bagi pengguna dengan role 'admin'.

    Memeriksa apakah pengguna saat ini telah login dan memiliki role 'admin'.
    Jika tidak memenuhi syarat, permintaan dibatalkan dengan respons HTTP 403
    (Forbidden). Digunakan pada rute administratif seperti manajemen wisata,
    event, paket, atau pengguna.

    Args:
        f (callable): Fungsi view Flask yang akan dilindungi.

    Returns:
        callable: Fungsi view yang telah dibungkus dengan logika otorisasi admin.

    Contoh Penggunaan:
        @admin.route('/admin/dashboard')
        @login_required
        @admin_required
        def dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) # HTTP status code untuk Forbidden
        return f(*args, **kwargs)
    return decorated_function