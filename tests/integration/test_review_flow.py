import pytest
from app import db
from app.models.review import Review


def test_unauthenticated_user_cannot_see_review_form(client, wisata_fixture):
    """Menguji visibilitas formulir review untuk pengguna yang belum terautentikasi.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    response = client.get(f'/wisata/detail/{wisata_item.id}')

    assert response.status_code == 200
    assert b'Login untuk Menulis Ulasan' in response.data
    assert b'Tulis Ulasan Anda' not in response.data


def test_authenticated_user_can_see_review_form(authenticated_client, wisata_fixture):
    """Menguji visibilitas formulir review untuk pengguna yang belum terautentikasi.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    response = authenticated_client.get(f'/wisata/detail/{wisata_item.id}')

    assert response.status_code == 200
    assert b'Kirim Review' in response.data
    assert b'Login untuk memberikan review' not in response.data


def test_user_can_submit_valid_review(authenticated_client, wisata_fixture, test_user):
    """Menguji proses pengiriman review yang valid oleh pengguna terautentikasi.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    wisata_item = wisata_fixture[0]
    review_data = {
        'rating': 5,
        'komentar': 'Pemandangan dari puncak sangat menakjubkan!'
    }

    response = authenticated_client.post(f'/wisata/detail/{wisata_item.id}',
                                         data=review_data, follow_redirects=True)

    assert response.status_code == 200
    assert b'Terima kasih! Review Anda telah ditambahkan.' in response.data
    assert b'Pemandangan dari puncak sangat menakjubkan!' in response.data

    review = Review.query.filter_by(user_id=user.id, wisata_id=wisata_item.id).first()
    assert review is not None
    assert review.rating == 5


def test_user_review_is_censored(authenticated_client, wisata_fixture):
    """Menguji integrasi filter kata-kata kotor (`censor_text`) saat pengguna mengirim review.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    review_data = {
        'rating': 2,
        'komentar': 'Tempatnya bagus, tapi fasilitasnya seperti babi.'
    }

    response = authenticated_client.post(f'/wisata/detail/{wisata_item.id}',
                                         data=review_data, follow_redirects=True)

    assert response.status_code == 200
    assert b'fasilitasnya seperti ****.' in response.data
    assert b'babi' not in response.data


def test_user_cannot_submit_invalid_review(authenticated_client, wisata_fixture):
    """Menguji validasi data formulir review (seperti rating di luar batas atau komentar kosong).

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    review_data = {
        'rating': 99,
        'komentar': ''
    }

    response = authenticated_client.post(f'/wisata/detail/{wisata_item.id}', data=review_data)

    assert response.status_code == 200
    assert b'Terima kasih! Review Anda telah ditambahkan.' not in response.data
    assert b'Rating harus antara 1 dan 5.' in response.data
    assert b'Komentar tidak boleh kosong.' in response.data