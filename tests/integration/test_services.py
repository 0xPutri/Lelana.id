import pytest
import os
import io
import base64
from werkzeug.datastructures import FileStorage
from app.services.file_handler import save_pictures


def test_save_pictures_valid_file(app, tmp_path):
    """Menguji fungsi `save_pictures` dengan skenario file gambar yang valid.

    Args:
        app: Instance aplikasi Flask
        tmp_path: Path sementara untuk pengujian
    """
    with app.app_context():
        app.config['UPLOAD_FOLDER'] = str(tmp_path)

        png_1x1_pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        fake_image_bytes = base64.b64decode(png_1x1_pixel_b64)
        file_stream = io.BytesIO(fake_image_bytes)

        picture = FileStorage(stream=file_stream, filename='test_image.png', content_type='image/png')

        saved_filenames = save_pictures([picture])

        assert len(saved_filenames) == 1
        saved_filename = saved_filenames[0]
        assert saved_filename.endswith('.png')

        expected_file_path = os.path.join(tmp_path, saved_filename)
        assert os.path.exists(expected_file_path)


def test_save_pictures_invalid_mime_type(app, tmp_path):
    """Menguji penanganan kesalahan ketika `save_pictures` menerima tipe MIME yang tidak diizinkan.

    Args:
        app: Instance aplikasi Flask
        tmp_path: Path sementara untuk pengujian
    """
    with app.app_context():
        app.config['UPLOAD_FOLDER'] = str(tmp_path)

        fake_text_bytes = b'ini adalah file teks biasa, bukan gambar.'
        file_stream = io.BytesIO(fake_text_bytes)

        picture = FileStorage(stream=file_stream, filename='fake_image.png', content_type='text/plain')

        with pytest.raises(ValueError) as excinfo:
            save_pictures([picture])

        assert 'Tipe file tidak valid' in str(excinfo.value)

        assert len(os.listdir(tmp_path)) == 0