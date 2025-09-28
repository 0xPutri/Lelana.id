import uuid
import os
import magic
from flask import current_app

def save_pictures(form_pictures):
    """
    Menyimpan file gambar yang diunggah ke direktori upload dengan validasi keamanan ganda.

    Setiap file diverifikasi berdasarkan tipe MIME aktual (bukan hanya ekstensi)
    menggunakan library python-magic untuk mencegah unggahan berbahaya.
    Setelah lolos validasi, file diberi nama unik (UUID4 + ekstensi asli) dan
    disimpan di folder UPLOAD_FOLDER. Nama file tidak disanitasi ulang karena
    ekstensi berasal dari MIME yang telah diverifikasi.

    Digunakan saat pengguna mengirim ulasan dengan foto atau admin mengelola konten.

    Args:
        form_pictures (list[FileStorage]): Daftar file dari MultipleFileField WTForms.

    Returns:
        list[str]: Daftar nama file yang berhasil disimpan (tanpa path), siap disimpan ke database.

    Raises:
        ValueError: Jika salah satu file memiliki tipe MIME yang tidak diizinkan
                    (hanya 'image/jpeg', 'image/png', dan 'image/gif' yang diterima).

    Catatan:
        Fungsi ini membaca 2048 byte pertama dari stream untuk deteksi MIME,
        lalu mengembalikan posisi stream ke awal agar file dapat disimpan utuh.
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