import os
import logging
from app import create_app, db


def test_production_config():
    """Uji bahwa konfigurasi 'production' memuat pengaturan yang benar."""
    logging.shutdown()
    app = create_app('production')
    assert not app.testing
    assert not app.debug
    assert app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite:///:memory:'


def test_factory_creates_app():
    """Uji bahwa factory berhasil membuat instance aplikasi."""
    app = create_app('testing')
    assert app is not None


def test_security_headers_applied(client):
    """Uji bahwa header keamanan diterapkan pada respons.

    Args:
        client: fixture klien uji Flask.
    """
    response = client.get('/')
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_production_logging():
    """Uji bahwa logging untuk produksi diinisialisasi dengan benar."""
    log_file = 'logs/lelana.log'
    log_dir = 'logs'

    logging.shutdown()

    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(log_dir) and not os.listdir(log_dir):
        os.rmdir(log_dir)

    app = create_app('production')

    try:
        assert os.path.exists(log_dir)
        assert os.path.exists(log_file)

        assert any(isinstance(h, logging.FileHandler) for h in app.logger.handlers)

    finally:
        logging.shutdown()

        if os.path.exists(log_file):
            os.remove(log_file)
        if os.path.exists(log_dir) and not os.listdir(log_dir):
            os.rmdir(log_dir)