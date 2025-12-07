import pytest
from app import db
from app.models.paket_wisata import PaketWisata
from app.models.wisata import Wisata


@pytest.fixture
def paket_wisata_fixture(app, wisata_fixture):
    """Fixture yang membuat dan menyimpan objek PaketWisata contoh di database.

    Args:
        app: Instance aplikasi Flask
        wisata_fixture: Fixture wisata untuk membuat relasi

    Returns:
        PaketWisata: Instance paket wisata yang telah disimpan ke database
    """
    paket = PaketWisata(
        nama="Paket Petualangan 3 Hari",
        deskripsi="Menjelajahi tiga destinasi unggulan dalam tiga hari.",
        harga=1500000,
        destinasi=wisata_fixture[:2]
    )

    db.session.add(paket)
    db.session.commit()
    return paket


def test_admin_can_create_paket_wisata(admin_client, wisata_fixture):
    """Menguji kemampuan pengguna 'admin' untuk membuat entri paket wisata baru.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        wisata_fixture: Fixture wisata untuk membuat relasi
    """
    wisata_ids = [str(w.id) for w in wisata_fixture]
    new_paket_data = {
        'nama': 'Paket Liburan Keluarga',
        'deskripsi': 'Liburan seru untuk seluruh anggota keluarga.',
        'harga': 2500000,
        'destinasi': wisata_ids,
        'is_promoted': 'y'
    }

    response = admin_client.post('/paket-wisata/tambah', data=new_paket_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Paket wisata baru berhasil ditambahkan!" in response.data

    paket = PaketWisata.query.filter_by(nama='Paket Liburan Keluarga').first()

    assert paket is not None
    assert paket.harga == 2500000
    assert paket.is_promoted is True
    assert len(paket.destinasi) == len(wisata_fixture)


def test_admin_can_edit_paket_wisata(admin_client, paket_wisata_fixture, wisata_fixture):
    """Menguji kemampuan pengguna 'admin' untuk memodifikasi detail paket wisata.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        paket_wisata_fixture: Fixture paket wisata untuk pengujian
        wisata_fixture: Fixture wisata untuk membuat relasi
    """
    edit_url = f'/paket-wisata/edit/{paket_wisata_fixture.id}'

    updated_wisata_ids = [str(wisata_fixture[-1].id)]

    updated_data = {
        'nama': 'Paket Petualangan Spesial V2',
        'deskripsi': paket_wisata_fixture.deskripsi,
        'harga': 1750000,
        'destinasi': updated_wisata_ids
    }

    response = admin_client.post(edit_url, data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Paket wisata berhasil diperbarui!" in response.data

    updated_paket = db.session.get(PaketWisata, paket_wisata_fixture.id)

    assert updated_paket.nama == 'Paket Petualangan Spesial V2'
    assert updated_paket.harga == 1750000
    assert updated_paket.is_promoted is False
    assert len(updated_paket.destinasi) == 1
    assert updated_paket.destinasi[0].id == wisata_fixture[-1].id


def test_admin_can_delete_paket_wisata(admin_client, paket_wisata_fixture):
    """Menguji kemampuan pengguna 'admin' untuk menghapus paket wisata dari sistem.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        paket_wisata_fixture: Fixture paket wisata untuk pengujian
    """
    paket_id_to_delete = paket_wisata_fixture.id
    delete_url = f'/paket-wisata/hapus/{paket_id_to_delete}'

    response = admin_client.post(delete_url, follow_redirects=True)
    assert response.status_code == 200
    assert b"Paket wisata telah berhasil dihapus" in response.data

    deleted_paket = db.session.get(PaketWisata, paket_id_to_delete)
    assert deleted_paket is None