import pytest
from flask_wtf import FlaskForm


def test_admin_can_view_manage_users_page(admin_client):
    """Menguji admin dapat melihat halaman manajemen pengguna.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/admin/users')
    assert response.status_code == 200
    assert b"Manajemen Pengguna" in response.data
    assert b"Daftar Pengguna" in response.data
    assert b"Username" in response.data


def test_admin_can_view_manage_wisata_page(admin_client):
    """Menguji admin dapat melihat halaman manajemen wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/admin/wisata')
    assert response.status_code == 200
    assert b"Manajemen Wisata" in response.data
    assert b"Daftar Wisata" in response.data


def test_admin_can_view_manage_event_page(admin_client):
    """Menguji admin dapat melihat halaman manajemen event.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/admin/event')
    assert response.status_code == 200
    assert b"Manajemen Event" in response.data
    assert b"Daftar Event" in response.data


def test_admin_can_view_manage_paket_wisata_page(admin_client):
    """Menguji admin dapat melihat halaman manajemen paket wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/admin/paket-wisata')
    assert response.status_code == 200
    assert b"Manajemen Paket Wisata" in response.data
    assert b"Daftar Paket Wisata" in response.data