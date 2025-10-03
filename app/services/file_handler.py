import uuid
import os
import magic
from flask import current_app

def save_pictures(form_pictures):
    """Menyimpan satu atau beberapa file gambar yang diunggah ke direktori upload.

    Fungsi ini melakukan validasi keamanan berbasis MIME type (bukan hanya ekstensi),
    menghasilkan nama file unik menggunakan UUID, dan menyimpan file ke lokasi
    yang dikonfigurasi di `UPLOAD_FOLDER`.

    Args:
        form_pictures (list[FileStorage]): Daftar objek file dari formulir Flask-WTF.

    Returns:
        list[str]: Daftar nama file yang berhasil disimpan (tanpa path lengkap).

    Raises:
        ValueError: Jika salah satu file bukan gambar dengan MIME type yang diizinkan
                    (hanya 'image/jpeg', 'image/png', 'image/gif').
    """
    saved_filenames = []

    allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']

    mime_checker = magic.Magic(mime=True)

    for picture in form_pictures:
        # 1. Validasi Konten File (MIME Type)
        file_head = picture.stream.read(2048)
        picture.stream.seek(0)

        detected_mime = mime_checker.from_buffer(file_head)

        if detected_mime not in allowed_mimes:
            raise ValueError(f'Tipe file tidak valid: terdeteksi {detected_mime}. Hanya gambar yang diizinkan.')
        
        # 2. Proses Penyimpanan File yang Aman
        _, f_ext = os.path.splitext(picture.filename)
        picture_fn = str(uuid.uuid4()) + f_ext

        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

        picture.save(picture_path)
        saved_filenames.append(picture_fn)

    return saved_filenames