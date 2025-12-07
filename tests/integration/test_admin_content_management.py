from app import db
from app.models.wisata import Wisata


def test_admin_can_create_wisata(admin_client):
    """Menguji kemampuan pengguna 'admin' untuk membuat entri destinasi wisata baru.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    new_wisata_data = {
        'nama': 'Pantai Menganti',
        'kategori': 'Alam',
        'lokasi': 'Kebumen, Jawa Tengah',
        'deskripsi': 'Pantai indah dengan pasir putih dan tebing.',
        'latitude': -7.77,
        'longitude': 109.5
    }

    response = admin_client.post('/wisata/tambah', data=new_wisata_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Destinasi wisata baru berhasil ditambahkan!" in response.data

    wisata = Wisata.query.filter_by(nama='Pantai Menganti').first()
    assert wisata is not None
    assert wisata.lokasi == 'Kebumen, Jawa Tengah'


def test_admin_can_edit_wisata(admin_client, wisata_fixture):
    """Menguji kemampuan pengguna 'admin' untuk memodifikasi data destinasi wisata yang sudah ada.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_to_edit = wisata_fixture[0]
    edit_url = f'/wisata/edit/{wisata_to_edit.id}'

    updated_data = {
        'nama': 'Curug Cipendok V2',
        'kategori': 'Air Terjun',
        'lokasi': 'Banyumas, Cilongok',
        'deskripsi': 'Deskripsi yang sudah diperbarui.'
    }

    response = admin_client.post(edit_url, data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Data wisata berhasil diperbarui!" in response.data

    updated_wisata = db.session.get(Wisata, wisata_to_edit.id)
    assert updated_wisata.nama == 'Curug Cipendok V2'
    assert updated_wisata.lokasi == 'Banyumas, Cilongok'


def test_admin_can_delete_wisata(admin_client, wisata_fixture):
    """Menguji kemampuan pengguna 'admin' untuk menghapus entri destinasi wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_to_delete = wisata_fixture[0]
    delete_url = f'/wisata/hapus/{wisata_to_delete.id}'

    response = admin_client.post(delete_url, follow_redirects=True)
    assert response.status_code == 200
    assert b"Data wisata telah berhasil dihapus." in response.data

    deleted_wisata = db.session.get(Wisata, wisata_to_delete.id)
    assert deleted_wisata is None