import pytest
from app import create_app, db
from app.models.user import User
from app.models.wisata import Wisata
from app.models.itinerari import Itinerari
from tests.helpers import AuthActions


@pytest.fixture(scope='function')
def app():
    """Fixture Pytest untuk menginisialisasi dan menyiapkan lingkungan aplikasi Flask.

    Fixture ini membuat instance aplikasi dengan konfigurasi 'testing',
    membuat semua tabel basis data, dan menghapus semua data (cleanup)
    setelah setiap pengujian selesai untuk menjamin isolasi data.

    Yields:
        Flask.app: Objek aplikasi Flask yang dikonfigurasi untuk pengujian.
    """
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture(scope='function')
def client(app):
    """Fixture Pytest yang menyediakan klien pengujian HTTP untuk membuat permintaan simulasi.

    Mengambil objek aplikasi Flask dari fixture `app` dan mengembalikan klien
    pengujian yang dapat digunakan untuk mensimulasikan permintaan GET, POST, dll.

    Args:
        app: Objek aplikasi Flask yang telah disiapkan dari fixture `app`.

    Returns:
        Flask.testing.FlaskClient: Klien pengujian HTTP untuk simulasi interaksi.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def auth(client):
    """Fixture Pytest untuk menyediakan helper aksi autentikasi (AuthActions) yang terikat.

    Menginisialisasi dan mengembalikan instance dari kelas `AuthActions`,
    membuat proses login/logout/register dalam pengujian menjadi lebih bersih
    dan mudah dibaca.

    Args:
        client: Klien pengujian HTTP untuk aksi autentikasi.

    Returns:
        AuthActions: Objek kelas `AuthActions` yang sudah terikat dengan klien.
    """
    return AuthActions(client)


@pytest.fixture(scope='function')
def test_user(app):
    """Fixture Pytest untuk membuat pengguna standar yang terkonfirmasi (non-admin) untuk pengujian.

    Membuat objek User baru, menetapkan kata sandi yang di-hash, dan menyimpannya
    ke basis data untuk digunakan dalam skenario pengujian autentikasi dasar.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks database.

    Yields:
        tuple[User, str]: Objek pengguna (`User`) dan kata sandi mentah (`str`)
                          yang digunakan untuk login dalam pengujian.
    """
    with app.app_context():
        user = User(username='pemilik', email='pemilik@lelana.my.id')
        user.password = 'TestPassword123!'
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()

        yield user, 'TestPassword123!'


@pytest.fixture(scope='function')
def admin_user(app):
    """Fixture Pytest untuk membuat pengguna dengan peran 'admin' yang terkonfirmasi.

    Membuat objek User dengan peran admin dan menyimpannya ke basis data,
    ditujukan untuk pengujian fungsionalitas yang memerlukan izin administrator.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks database.

    Yields:
        tuple[User, str]: Objek pengguna admin (`User`) dan kata sandi mentah (`str`)
                          untuk pengujian otorisasi dan hak akses.
    """
    with app.app_context():
        user = User(username='admin', email='admin@lelana.my.id', role='admin')
        user.password = 'AdminPassword123!'
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()

        yield user, 'AdminPassword123!'


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Fixture Pytest yang menyediakan klien HTTP dalam keadaan sudah login sebagai pengguna standar.

    Menggunakan fixture `test_user` dan helper `AuthActions` untuk
    melakukan login pengguna standar secara otomatis sebelum menjalankan tes
    yang memerlukan sesi aktif.

    Args:
        client: Klien pengujian HTTP yang belum diautentikasi.
        test_user: Tuple (User, str) dari fixture `test_user`.

    Returns:
        Flask.testing.FlaskClient: Klien pengujian HTTP yang sudah terautentikasi.
    """
    user, password = test_user
    auth = AuthActions(client)
    auth.login(user.email, password)

    return client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    """Fixture Pytest yang menyediakan klien HTTP dalam keadaan sudah login sebagai administrator sistem.

    Menggunakan fixture `admin_user` dan helper `AuthActions` untuk
    melakukan login pengguna admin secara otomatis sebelum menjalankan tes
    yang memerlukan izin administratif.

    Args:
        client: Klien pengujian HTTP yang belum diautentikasi.
        admin_user: Tuple (User, str) dari fixture `admin_user`.

    Returns:
        Flask.testing.FlaskClient: Klien pengujian HTTP yang sudah terautentikasi sebagai admin.
    """
    user, password = admin_user
    auth = AuthActions(client)
    auth.login(user.email, password)

    return client


@pytest.fixture(scope='function')
def test_user2(app):
    """Fixture Pytest untuk membuat pengguna standar kedua (pengganggu/secondary user) yang terkonfirmasi.

    Digunakan dalam skenario pengujian izin dan kepemilikan data
    (misalnya, pengguna A tidak boleh mengubah data pengguna B) untuk skenario keamanan.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks database.

    Yields:
        User: Objek pengguna kedua (`User`) yang sudah tersimpan di database.
    """
    with app.app_context():
        user = User(username='pengganggu', email='pengganggu@lelana.my.id')
        user.password = 'TestPassword123!'
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()

        yield user


@pytest.fixture(scope='function')
def wisata_fixture(app):
    """Fixture Pytest untuk mengisi basis data dengan data objek Wisata contoh yang relevan.

    Membuat dan menyimpan dua objek `Wisata` (Curug Cipendok dan Baturraden)
    sebagai data awal untuk pengujian fungsionalitas terkait tempat wisata.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks database.

    Yields:
        list[Wisata]: Daftar objek `Wisata` yang telah disimpan di basis data.
    """
    with app.app_context():
        wisata1 = Wisata(nama='Curug Cipendok', kategori='Alam', lokasi='Banyumas', deskripsi='Air terjun.')
        wisata2 = Wisata(nama='Baturraden', kategori='Alam', lokasi='Banyumas', deskripsi='Pemandian air panas.')
        db.session.add_all([wisata1, wisata2])
        db.session.commit()

        yield [wisata1, wisata2]


@pytest.fixture(scope='function')
def itinerari_fixture(app, test_user, wisata_fixture):
    """Fixture Pytest untuk membuat objek Itinerari yang terkait dengan pengguna dan wisata contoh.

    Membuat Itinerari baru ('Trip Banyumas'), mengaitkannya dengan `test_user`
    dan salah satu objek dari `wisata_fixture`, lalu menyimpannya ke basis data.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks database.
        test_user: Tuple (User, str) dari fixture `test_user`.
        wisata_fixture: Daftar objek `Wisata` dari fixture `wisata_fixture`.

    Yields:
        Itinerari: Objek Itinerari yang telah tersimpan di basis data dan siap diuji.
    """
    with app.app_context():
        user, _ = test_user
        user_id = user.id
        wisata_id = wisata_fixture[0].id

        user_from_db = db.session.get(User, user_id)
        wisata_from_db = db.session.get(Wisata, wisata_id)

        it = Itinerari(
            judul='Trip Banyumas',
            deskripsi='Jalan-jalan seru',
            penulis=user_from_db,
            wisata_termasuk=[wisata_from_db]
        )
        db.session.add(it)
        db.session.commit()

        yield it