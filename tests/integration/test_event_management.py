import pytest
from datetime import datetime, timedelta, timezone
from app import db
from app.models.event import Event


@pytest.fixture
def event_fixture(app):
    """Fixture yang membuat dan menyimpan objek Event contoh di database.

    Args:
        app: Instance aplikasi Flask

    Returns:
        Event: Instance event yang telah disimpan ke database
    """
    event = Event(
        nama="Festival Jazz Tahunan",
        tanggal=datetime.now(timezone.utc) + timedelta(days=30),
        lokasi="Alun-alun Kota",
        deskripsi="Acara musik jazz tahunan dengan bintang tamu internasional.",
        penyelenggara="Dinas Pariwisata Kota"
    )
    db.session.add(event)
    db.session.commit()
    return event


def test_admin_can_create_event(admin_client):
    """Menguji kemampuan pengguna 'admin' untuk membuat entri acara/event baru.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    new_event_data = {
        'nama': 'Pameran Kuliner Nusantara',
        'tanggal': (datetime.now(timezone.utc) + timedelta(days=15)).strftime('%Y-%m-%d'),
        'lokasi': 'Lapangan Utama',
        'deskripsi': 'Menampilkan makanan khas dari seluruh Indonesia.',
        'penyelenggara': 'Komunitas Kuliner'
    }

    response = admin_client.post('/event/tambah', data=new_event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event baru berhasil ditambahkan!" in response.data

    event = Event.query.filter_by(nama='Pameran Kuliner Nusantara').first()
    assert event is not None
    assert event.lokasi == 'Lapangan Utama'


def test_admin_can_edit_event(admin_client, event_fixture):
    """Menguji kemampuan pengguna 'admin' untuk memodifikasi data detail event yang sudah ada.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        event_fixture: Fixture event untuk pengujian
    """
    edit_url = f'/event/edit/{event_fixture.id}'
    updated_data = {
        'nama': 'Festival Jazz Internasional',
        'tanggal': event_fixture.tanggal.strftime('%Y-%m-%d'),
        'lokasi': 'Gedung Konser Kota',
        'deskripsi': 'Deskripsi acara yang telah diperbarui.',
        'penyelenggara': event_fixture.penyelenggara
    }

    response = admin_client.post(edit_url, data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Data event berhasil diperbarui!" in response.data

    updated_event = db.session.get(Event, event_fixture.id)
    assert updated_event.nama == 'Festival Jazz Internasional'
    assert updated_event.lokasi == 'Gedung Konser Kota'


def test_admin_can_delete_event(admin_client, event_fixture):
    """Menguji kemampuan pengguna 'admin' untuk menghapus event dari sistem.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        event_fixture: Fixture event untuk pengujian
    """
    event_id_to_delete = event_fixture.id
    delete_url = f'/event/hapus/{event_id_to_delete}'

    response = admin_client.post(delete_url, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event telah berhasil dihapus." in response.data

    deleted_event = db.session.get(Event, event_id_to_delete)
    assert deleted_event is None