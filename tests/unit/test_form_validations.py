import pytest
from unittest.mock import MagicMock, patch
from wtforms.validators import ValidationError
from app.forms import RegistrationForm

@pytest.fixture
def registration_form(app):
    """Fixture Pytest untuk menyediakan instance dari RegistrationForm.

    Args:
        app: Objek aplikasi Flask untuk konteks.

    Yields:
        RegistrationForm: Objek formulir pendaftaran yang siap untuk diuji.
    """
    with app.app_context():
        yield RegistrationForm()


def test_validate_email_allowed_domain(app, registration_form):
    """Menguji skenario ketika email menggunakan domain yang secara eksplisit diizinkan.

    Args:
        app: Instance aplikasi Flask
        registration_form: Instance formulir registrasi
    """
    with app.app_context():
        app.config['ALLOWED_EMAIL_DOMAINS'] = ['gmail.com', 'yahoo.com']

        email_field = MagicMock()
        email_field.data = 'test@gmail.com'

        with patch('app.forms.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            try:
                registration_form.validate_email(email_field)
            except ValidationError:
                pytest.fail("Email dengan domain yang diizinkan seharusnya tidak memunculkan ValidationError.")


def test_validate_email_disallowed_domain(app, registration_form):
    """Menguji skenario ketika email menggunakan domain yang tidak diizinkan oleh konfigurasi.

    Args:
        app: Instance aplikasi Flask
        registration_form: Instance formulir registrasi
    """
    with app.app_context():
        app.config['ALLOWED_EMAIL_DOMAINS'] = ['gmail.com', 'yahoo.com']

        email_field = MagicMock()
        email_field.data = 'test@temp-mail.org'

        with pytest.raises(ValidationError, match='Pendaftaran hanya diizinkan untuk domain email populer'):
            registration_form.validate_email(email_field)


def test_validate_password_strong(registration_form):
    """Menguji skenario password yang memenuhi semua persyaratan keamanan (kuat).

    Args:
        registration_form: Instance formulir registrasi
    """
    password_field = MagicMock()
    password_field.data = 'StrongP@ss1'

    try:
        registration_form.validate_password(password_field)
    except ValidationError:
        pytest.fail("Password yang memenuhi seluruh kriteria keamanan seharusnya tidak memunculkan ValidationError.")


def test_validate_password_weak_no_uppercase(registration_form):
    """Menguji skenario password lemah karena tidak memiliki setidaknya satu huruf besar.

    Args:
        registration_form: Instance formulir registrasi
    """
    password_field = MagicMock()
    password_field.data = 'weakpass1@'

    with pytest.raises(ValidationError, match='Password harus mengandung setidaknya satu huruf besar.'):
        registration_form.validate_password(password_field)


def test_validate_password_weak_no_lowercase(registration_form):
    """Menguji skenario password lemah karena tidak memiliki setidaknya satu huruf kecil.

    Args:
        registration_form: Instance formulir registrasi
    """
    password_field = MagicMock()
    password_field.data = 'WEAKPASS1@'

    with pytest.raises(ValidationError, match='Password harus mengandung setidaknya satu huruf kecil.'):
        registration_form.validate_password(password_field)


def test_validate_password_weak_no_digit(registration_form):
    """Menguji skenario password lemah karena tidak memiliki setidaknya satu angka (digit).

    Args:
        registration_form: Instance formulir registrasi
    """
    password_field = MagicMock()
    password_field.data = 'WeakPass@'

    with pytest.raises(ValidationError, match='Password harus mengandung setidaknya satu angka.'):
        registration_form.validate_password(password_field)


def test_validate_password_weak_no_special_char(registration_form):
    """Menguji skenario password lemah karena tidak memiliki setidaknya satu karakter spesial.

    Args:
        registration_form: Instance formulir registrasi
    """
    password_field = MagicMock()
    password_field.data = 'WeakPass1'

    with pytest.raises(ValidationError, match='Password harus mengandung setidaknya satu karakter spesial'):
        registration_form.validate_password(password_field)