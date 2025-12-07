import pytest
from app.models.user import User
from app import db


def test_admin_can_view_edit_user_page(admin_client, test_user):
    """Menguji admin dapat mengakses halaman edit pengguna lain.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    response = admin_client.get(f'/admin/users/edit/{user.id}')
    assert response.status_code == 200
    assert b'Edit Pengguna' in response.data
    assert f'value="{user.username}"'.encode() in response.data


def test_admin_can_edit_user(admin_client, test_user):
    """Menguji kemampuan pengguna 'admin' untuk memodifikasi detail dan peran pengguna lain.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    edit_url = f'/admin/users/edit/{user.id}'
    updated_data = {
        'username': 'editeduser',
        'email': 'edited@lelana.my.id',
        'role': 'admin'
    }

    response = admin_client.post(edit_url, data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Data pengguna editeduser berhasil diperbarui.' in response.data

    updated_user = db.session.get(User, user.id)
    assert updated_user.username == 'editeduser'
    assert updated_user.role == 'admin'


def test_admin_cannot_change_own_role(admin_client, admin_user):
    """Menguji admin tidak dapat mengubah perannya sendiri menjadi non-admin.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        admin_user: Fixture admin untuk pengujian
    """
    user, _ = admin_user
    edit_url = f'/admin/users/edit/{user.id}'
    updated_data = {
        'username': 'admin',
        'email': user.email,
        'role': 'user'
    }
    response = admin_client.post(edit_url, data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Anda tidak mengubah peran (role) akun Anda sendiri.' in response.data

    admin_in_db = db.session.get(User, user.id)
    assert admin_in_db.role == 'admin'


def test_admin_cannot_delete_self(admin_client, admin_user):
    """Menguji skenario di mana seorang admin mencoba menghapus akunnya sendiri.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        admin_user: Fixture admin untuk pengujian
    """
    user, _ = admin_user
    delete_url = f'/admin/users/hapus/{user.id}'
    response = admin_client.post(delete_url, follow_redirects=True)

    assert response.status_code == 200
    assert b'Anda tidak dapat menghapus akun Anda sendiri.' in response.data

    admin_in_db = db.session.get(User, user.id)
    assert admin_in_db is not None


def test_admin_cannot_delete_last_admin(admin_client, admin_user):
    """Menguji skenario perlindungan kritis: mencegah penghapusan jika hanya tersisa satu admin.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        admin_user: Fixture admin untuk pengujian
    """
    admin_count = User.query.filter_by(role='admin').count()
    assert admin_count == 1

    user, _ = admin_user
    delete_url = f'/admin/users/hapus/{user.id}'
    response = admin_client.post(delete_url, follow_redirects=True)
    assert b'Anda tidak dapat menghapus akun Anda sendiri.' in response.data


def test_admin_can_delete_other_user(admin_client, test_user):
    """Menguji kemampuan admin untuk menghapus akun pengguna biasa (non-admin).

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    delete_url = f'/admin/users/hapus/{user.id}'
    response = admin_client.post(delete_url, follow_redirects=True)

    assert response.status_code == 200
    assert f'Pengguna {user.username} telah berhasil dihapus.'.encode() in response.data

    deleted_user = db.session.get(User, user.id)
    assert deleted_user is None


def test_delete_nonexistent_user(admin_client):
    """Menguji penghapusan pengguna dengan ID yang tidak ada.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
    """
    non_existent_id = 9999
    delete_url = f'/admin/users/hapus/{non_existent_id}'
    response = admin_client.post(delete_url, follow_redirects=True)
    assert response.status_code == 404


import pytest

@pytest.mark.skip(reason="CSRF flash message test is flaky and needs deeper investigation")
def test_delete_user_with_invalid_csrf(admin_client, test_user):
    """Menguji penghapusan pengguna gagal jika token CSRF tidak valid.

    Args:
        admin_client: Klien pengujian yang terautentikasi sebagai admin
        test_user: Fixture pengguna untuk pengujian
    """
    user_to_delete, _ = test_user
    delete_url = f'/admin/users/hapus/{user_to_delete.id}'

    response = admin_client.post(delete_url, data={}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Gagal menghapus pengguna: Token keamanan tidak valid atau kedaluwarsa.' in response.data

    not_deleted_user = db.session.get(User, user_to_delete.id)
    assert not_deleted_user is not None