from unittest.mock import patch
from app.models.user import User
from app import db


def test_get_register_page(client):
    """Menguji akses ke halaman pendaftaran akun pengguna baru.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Buat Akun Baru' in response.data


def test_successful_registration(auth):
    """Menguji skenario pendaftaran pengguna baru yang sukses dan valid.

    Args:
        auth: Objek AuthActions untuk melakukan registrasi
    """
    response = auth.register('newuser', 'new@lelana.my.id', 'NewPassword123!', 'NewPassword123!')

    assert response.status_code == 200
    assert b'Registrasi berhasil! Email konfirmasi telah dikirim. Silakan periksa email Anda.' in response.data
    assert b'Logout' in response.data


def test_registration_with_existing_email(auth, test_user):
    """Menguji pendaftaran dengan email yang sudah ada.

    Args:
        auth: Objek AuthActions untuk melakukan registrasi
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    response = auth.register('anotheruser', user.email, 'AnotherPassword123!', 'AnotherPassword123!')
    assert response.status_code == 200
    assert b'Email konfirmasi telah dikirim' in response.data


def test_get_login_page(client):
    """Menguji akses ke halaman form login pengguna.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login_page_when_already_logged_in(authenticated_client):
    """Menguji akses ke halaman login oleh pengguna yang sudah login.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
    """
    response = authenticated_client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_successful_login(auth, test_user):
    """Menguji skenario login pengguna terdaftar yang berhasil.

    Args:
        auth: Objek AuthActions untuk melakukan login
        test_user: Fixture pengguna untuk pengujian
    """
    user, password = test_user
    response = auth.login(user.email, password)

    assert response.status_code == 200
    assert b'Login berhasil!' in response.data
    assert b'Selamat Datang di Lelana.id' in response.data


def test_login_with_invalid_password(auth, test_user):
    """Menguji percobaan login menggunakan email yang benar tetapi password yang salah.

    Args:
        auth: Objek AuthActions untuk melakukan login
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    response = auth.login(user.email, 'WrongPassword!')

    assert response.status_code == 200
    assert b'Login gagal.' in response.data


def test_logout(auth, test_user):
    """Menguji fungsionalitas logout setelah pengguna berhasil login.

    Args:
        auth: Objek AuthActions untuk melakukan logout
        test_user: Fixture pengguna untuk pengujian
    """
    user, password = test_user
    auth.login(user.email, password)
    response = auth.logout()

    assert response.status_code == 200
    assert b'Anda telah berhasil logout.' in response.data
    assert b'Login' in response.data


def test_unconfirmed_user_redirect(client, app):
    """Menguji bahwa pengguna yang belum terkonfirmasi di-redirect ke halaman unconfirmed.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        app: Instance aplikasi Flask
    """
    with app.app_context():
        user = User(username='unconfirmed_user', email='unconfirmed@test.com', is_confirmed=False)
        user.password = 'password'
        db.session.add(user)
        db.session.commit()

    client.post('/auth/login', data={'email': 'unconfirmed@test.com', 'password': 'password'}, follow_redirects=True)

    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/auth/unconfirmed'

    response_unconfirmed = client.get(response.location)
    assert b'Konfirmasi Akun Anda' in response_unconfirmed.data


def test_resend_confirmation_email(authenticated_client):
    """Menguji pengiriman ulang email konfirmasi.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
    """
    with patch('app.routes.auth_routes.send_email') as mock_send_email:
        response = authenticated_client.get('/auth/confirm', follow_redirects=True)
        assert response.status_code == 200
        assert b'Email konfirmasi baru telah dikirimkan.' in response.data
        mock_send_email.assert_called_once()


def test_confirmed_user_access_unconfirmed_page(authenticated_client):
    """Menguji pengguna yang sudah terkonfirmasi mengakses halaman unconfirmed.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
    """
    response = authenticated_client.get('/auth/unconfirmed', follow_redirects=True)
    assert response.status_code == 200
    assert b'Selamat Datang di Lelana.id' in response.data


def test_password_reset_request_get_page(client):
    """WHITEBOX TEST: Menguji akses GET ke halaman permintaan reset password.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/auth/reset-password')
    assert response.status_code == 200
    assert b'Reset Password' in response.data


def test_password_reset_request_as_logged_in_user(auth, test_user, client):
    """WHITEBOX TEST: Menguji akses ke halaman permintaan reset oleh pengguna yang sudah login.

    Args:
        auth: Objek AuthActions untuk login
        test_user: Fixture pengguna untuk pengujian
        client: Klien pengujian yang tidak terautentikasi
    """
    user, password = test_user
    auth.login(user.email, password)
    response = client.get('/auth/reset-password', follow_redirects=True)
    assert b'Selamat Datang di Lelana.id' in response.data


@patch('app.routes.auth_routes.send_email')
def test_password_reset_request_submit_valid_email(mock_send_email, client, test_user):
    """WHITEBOX TEST: Menguji pengiriman form permintaan reset dengan email valid.

    Args:
        mock_send_email: Mock untuk fungsi send_email
        client: Klien pengujian yang tidak terautentikasi
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    response = client.post('/auth/reset-password', data={'email': user.email}, follow_redirects=True)
    assert response.status_code == 200
    assert b'instruksi reset password telah dikirim' in response.data
    mock_send_email.assert_called_once()


@patch('app.routes.auth_routes.send_email')
def test_password_reset_request_submit_invalid_email(mock_send_email, client):
    """WHITEBOX TEST: Menguji pengiriman form permintaan reset dengan email tidak valid.

    Args:
        mock_send_email: Mock untuk fungsi send_email
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.post('/auth/reset-password', data={'email': 'nobody@example.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'instruksi reset password telah dikirim' in response.data
    mock_send_email.assert_not_called()


def test_password_reset_with_invalid_token(client):
    """WHITEBOX TEST: Menguji akses ke halaman reset dengan token tidak valid.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/auth/reset-password/invalid-token', follow_redirects=True)
    assert response.status_code == 200
    assert b'Tautan reset password tidak valid' in response.data


def test_password_reset_with_valid_token_and_update(client, auth, test_user, app):
    """WHITEBOX TEST: Menguji seluruh alur reset password dengan token valid.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        auth: Objek AuthActions untuk login
        test_user: Fixture pengguna untuk pengujian
        app: Instance aplikasi Flask
    """
    user, old_password = test_user

    with app.app_context():
        token = user.generate_reset_token()

    response_get = client.get(f'/auth/reset-password/{token}')
    assert response_get.status_code == 200
    assert b'Atur Ulang Password Anda' in response_get.data

    new_password = 'a_brand_new_password'
    response_post = client.post(f'/auth/reset-password/{token}', data={
        'password': new_password,
        'confirm_password': new_password
    }, follow_redirects=False)

    assert response_post.status_code == 302
    assert response_post.location == '/auth/login'

    response_login_page = client.get(response_post.location)
    assert response_login_page.status_code == 200
    assert b'Password Anda telah berhasil direset' in response_login_page.data

    response_fail = auth.login(user.email, old_password)
    assert b'Login gagal' in response_fail.data

    response_success = auth.login(user.email, new_password)
    assert b'Login berhasil' in response_success.data


def test_password_reset_page_as_logged_in_user(authenticated_client, app, test_user):
    """Menguji akses ke halaman reset password dengan token oleh pengguna yang sudah login.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        app: Instance aplikasi Flask
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    with app.app_context():
        token = user.generate_reset_token()

    response = authenticated_client.get(f'/auth/reset-password/{token}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Selamat Datang di Lelana.id' in response.data