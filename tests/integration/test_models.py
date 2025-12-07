import pytest
from app import db
from app.models.user import User
from app.models.wisata import Wisata
from app.models.review import Review
from app.models.itinerari import Itinerari
import time


def test_create_user(app):
    """Menguji fungsionalitas pembuatan dan persistensi objek User (Pengguna) baru.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='testuser', email='test@lelana.my.id')
        user.password = 'Password123!'
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(email='test@lelana.my.id').first()

        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
        assert retrieved_user.email == 'test@lelana.my.id'
        assert retrieved_user.password_hash is not None
        assert retrieved_user.role == 'user'


def test_password_hashing(app):
    """Menguji mekanisme hashing password untuk keamanan.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='putri', email='putri@lelana.my.id')
        user.password = 'supersecret'

        with pytest.raises(AttributeError):
            _ = user.password


def test_password_verification(app):
    """Menguji fungsionalitas verifikasi password ter-hash.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='ayu', email='ayu@lelana.my.id')
        user.password = 'Ayu123'
        db.session.add(user)
        db.session.commit()

        assert user.verify_password('Ayu123') is True
        assert user.verify_password('ayu123') is False


def test_user_repr(app):
    """Menguji metode __repr__ pada model User.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='repr_user', email='repr@lelana.my.id')
        assert repr(user) == '<User repr_user>'


def test_confirmation_token_flow(app):
    """Menguji alur pembuatan dan verifikasi token konfirmasi email.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='unconfirmed', email='unconfirmed@lelana.my.id')
        db.session.add(user)
        db.session.commit()

        assert not user.is_confirmed

        token = user.generate_confirmation_token()
        assert token is not None

        confirmed_user = User.confirm(token)
        assert confirmed_user == user
        assert user.is_confirmed


def test_invalid_confirmation_token(app):
    """Menguji verifikasi token konfirmasi yang tidak valid.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        invalid_user = User.confirm('this-is-not-a-valid-token')
        assert invalid_user is None


def test_expired_confirmation_token(app):
    """Menguji verifikasi token konfirmasi yang sudah kedaluwarsa.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='expiring', email='expiring@lelana.my.id')
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()

        expired_user = User.confirm(token, expiration=-1)
        assert expired_user is None


def test_reset_token_flow(app):
    """Menguji alur pembuatan dan verifikasi token reset password.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='reset_user', email='reset@lelana.my.id')
        db.session.add(user)
        db.session.commit()

        token = user.generate_reset_token()
        assert token is not None

        verified_user = User.verify_reset_token(token)
        assert verified_user == user


def test_invalid_reset_token(app):
    """Menguji verifikasi token reset yang tidak valid.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        invalid_user = User.verify_reset_token('this-is-not-a-valid-token')
        assert invalid_user is None


def test_create_wisata(app):
    """Menguji fungsionalitas pembuatan dan persistensi objek Wisata (Destinasi).

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        wisata = Wisata(
            nama='Curug Cipendok',
            kategori='Alam',
            lokasi='Cilongok, Banyumas',
            deskripsi='Air terjun yang indah di kaki Gunung Slamet.'
        )
        db.session.add(wisata)
        db.session.commit()

        retrieved_wisata = Wisata.query.filter_by(nama='Curug Cipendok').first()

        assert retrieved_wisata is not None
        assert retrieved_wisata.kategori == 'Alam'
        assert "Gunung Slamet" in retrieved_wisata.deskripsi


def test_user_review_relationship(app):
    """Menguji relasi One-to-Many antara model User dan Review.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='reviewer', email='reviewer@lelana.my.id', password_hash='xyz')
        wisata = Wisata(nama='Baturaden', kategori='Alam', lokasi='Banyumas', deskripsi='...')
        review = Review(rating=5, komentar='Sangat bagus!', author=user, wisata_reviewed=wisata)

        db.session.add_all([user, wisata, review])
        db.session.commit()

        assert user.reviews.count() == 1
        assert user.reviews.first().komentar == 'Sangat bagus!'
        assert review.author.username == 'reviewer'
        assert wisata.reviews.first().rating == 5


def test_itinerari_wisata_relationship(app):
    """Menguji relasi Many-to-Many antara model Itinerari dan Wisata.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='planner', email='planner@lelana.my.id', password_hash='abc')
        wisata1 = Wisata(nama='Wisata A', kategori='Budaya', lokasi='...', deskripsi='...')
        wisata2 = Wisata(nama='Wisata B', kategori='Kuliner', lokasi='...', deskripsi='...')

        itinerari = Itinerari(judul='Trip 2 Hari', penulis=user)
        itinerari.wisata_termasuk.append(wisata1)
        itinerari.wisata_termasuk.append(wisata2)

        db.session.add_all([user, wisata1, wisata2, itinerari])
        db.session.commit()

        assert len(itinerari.wisata_termasuk) == 2
        assert wisata1 in itinerari.wisata_termasuk
        assert itinerari in wisata2.termasuk_dalam_itinerari


def test_cascade_delete_on_user(app):
    """Menguji aturan cascade delete pada relasi User dan objek terkait (seperti Review).

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='todelete', email='del@lelana.my.id', password_hash='123')
        wisata = Wisata(nama='Lokasi Uji', kategori='Test', lokasi='...', deskripsi='...')
        review = Review(rating=1, komentar='Akan dihapus', author=user, wisata_reviewed=wisata)

        db.session.add_all([user, wisata, review])
        db.session.commit()

        user_id = user.id
        review_id = review.id

        assert db.session.get(User, user_id) is not None
        assert db.session.get(Review, review_id) is not None

        db.session.delete(user)
        db.session.commit()

        assert db.session.get(User, user_id) is None
        assert db.session.get(Review, review_id) is None