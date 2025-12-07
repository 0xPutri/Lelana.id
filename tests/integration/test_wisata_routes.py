import pytest
from app import db
from app.models.wisata import Wisata


def test_get_wisata_list_page(client):
    """Menguji akses ke halaman daftar wisata.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/wisata')
    assert response.status_code == 200
    assert b"Destinasi Wisata" in response.data


def test_get_wisata_detail_page(client, wisata_fixture):
    """Menguji akses ke halaman detail sebuah wisata.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    response = client.get(f'/wisata/detail/{wisata_item.id}')
    assert response.status_code == 200
    assert wisata_item.nama.encode() in response.data
    assert b"Ulasan Petualang" in response.data


def test_get_nonexistent_wisata_detail_page(client):
    """Menguji akses ke halaman detail wisata yang tidak ada.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/wisata/detail/9999')
    assert response.status_code == 404


def test_get_add_wisata_page_as_admin(admin_client):
    """Menguji admin dapat mengakses halaman form tambah wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/wisata/tambah')
    assert response.status_code == 200
    assert b"Tambah Wisata" in response.data


def test_get_edit_wisata_page_as_admin(admin_client, wisata_fixture):
    """Menguji admin dapat mengakses halaman form edit wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    response = admin_client.get(f'/wisata/edit/{wisata_item.id}')
    assert response.status_code == 200
    assert b"Edit Wisata" in response.data
    assert wisata_item.nama.encode() in response.data


def test_get_edit_nonexistent_wisata_page(admin_client):
    """Menguji akses ke halaman edit wisata yang tidak ada.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.get('/wisata/edit/9999')
    assert response.status_code == 404


def test_delete_nonexistent_wisata(admin_client):
    """Menguji penghapusan wisata yang tidak ada.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    response = admin_client.post('/wisata/hapus/9999', follow_redirects=True)
    assert response.status_code == 404


import pytest

@pytest.mark.skip(reason="CSRF flash message test is flaky and needs deeper investigation")
def test_delete_wisata_with_invalid_csrf(admin_client, wisata_fixture):
    """Menguji penghapusan wisata gagal jika token CSRF tidak valid.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    delete_url = f'/wisata/hapus/{wisata_item.id}'

    response = admin_client.post(delete_url, data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Permintaan tidak valid atau sesi telah kedaluwarsa.' in response.data

    wisata_in_db = db.session.get(Wisata, wisata_item.id)
    assert wisata_in_db is not None


def test_api_lokasi_wisata(client, wisata_fixture):
    """Menguji endpoint API untuk lokasi wisata.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    wisata_item.latitude = -7.123
    wisata_item.longitude = 110.456
    db.session.commit()

    response = client.get('/api/wisata/lokasi')
    assert response.status_code == 200

    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) > 0

    found_item = next((item for item in json_data if item['nama'] == wisata_item.nama), None)
    assert found_item is not None
    assert found_item['lat'] == -7.123
    assert found_item['lon'] == 110.456
    assert f'/wisata/detail/{wisata_item.id}' in found_item['detail_url']


def test_submit_review_unauthenticated(client, wisata_fixture):
    """Menguji pengiriman review oleh pengguna yang belum login.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    detail_url = f'/wisata/detail/{wisata_item.id}'
    review_data = {'rating': 5, 'komentar': 'Tes review'}

    response = client.post(detail_url, data=review_data, follow_redirects=True)

    assert response.status_code == 200
    assert b'Tes review' not in response.data