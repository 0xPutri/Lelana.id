import pytest


def test_admin_dashboard_unauthenticated(client):
    """Menguji akses ke dashboard admin oleh pengguna yang belum terautentikasi.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/admin/dashboard', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Panel Admin" not in response.data


def test_admin_dashboard_as_normal_user(authenticated_client):
    """Menguji akses ke dashboard admin oleh pengguna biasa (non-admin).

    Args:
        authenticated_client: Klien pengujian yang terautentikasi sebagai pengguna biasa
    """
    response = authenticated_client.get('/admin/dashboard')
    assert response.status_code == 403
    assert b"Akses Ditolak" in response.data


def test_admin_dashboard_as_admin_user(admin_client):
    """Menguji akses ke dashboard admin oleh pengguna dengan peran 'admin'.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/admin/dashboard')

    assert response.status_code == 200
    assert b"<title>Dashboard - Lelana.id</title>" in response.data