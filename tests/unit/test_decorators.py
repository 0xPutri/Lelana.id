import pytest
from unittest.mock import MagicMock, patch
from werkzeug.exceptions import Forbidden
from app.utils.decorators import admin_required


@admin_required
def dummy_view():
    """Fungsi tampilan (view function) placeholder yang dihias dengan `@admin_required`.

    Fungsi ini digunakan sebagai target uji untuk memverifikasi apakah dekorator
    `admin_required` berfungsi dengan benar dalam mengizinkan atau menolak akses.
    """
    return "OK"


def test_admin_required_with_admin_user():
    """Menguji dekorator `admin_required` ketika pengguna yang mengakses memiliki peran 'admin'.

    Memastikan bahwa pengguna yang terautentikasi dan memiliki peran 'admin'
    diizinkan untuk mengakses fungsi tampilan (`dummy_view`) tanpa memicu
    eksepsi `Forbidden` (HTTP 403).
    """
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = 'admin'

    with patch('app.utils.decorators.current_user', mock_user):
        try:
            result = dummy_view()
            assert result == "OK"
        except Forbidden:
            pytest.fail("Pengguna admin yang sudah terautentikasi seharusnya dapat mengakses view tanpa memunculkan Forbidden exception.")


def test_admin_required_with_non_admin_user():
    """Menguji dekorator `admin_required` ketika pengguna yang mengakses memiliki peran 'user' biasa.

    Memastikan bahwa pengguna yang terautentikasi tetapi tidak memiliki peran 'admin'
    secara tepat dicegah untuk mengakses fungsi tampilan, dan memicu eksepsi `Forbidden` (HTTP 403).
    """
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = 'user'

    with patch('app.utils.decorators.current_user', mock_user):
        with pytest.raises(Forbidden):
            dummy_view()


def test_admin_required_with_unauthenticated_user():
    """Menguji dekorator `admin_required` ketika pengguna tidak terautentikasi.

    Memastikan bahwa pengguna yang belum *login* (tidak terautentikasi)
    dicegah untuk mengakses fungsi tampilan, dan memicu eksepsi `Forbidden` (HTTP 403).
    """
    mock_user = MagicMock()
    mock_user.is_authenticated = False
    mock_user.role = 'user'

    with patch('app.utils.decorators.current_user', mock_user):
        with pytest.raises(Forbidden):
            dummy_view()