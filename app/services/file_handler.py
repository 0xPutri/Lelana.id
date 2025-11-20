import uuid
import os
import magic
from flask import current_app

def save_pictures(form_pictures):
    """Memvalidasi dan menyimpan file gambar yang diunggah dengan aman.

    Fungsi ini memproses daftar file yang diunggah, melakukan validasi keamanan
    berbasis tipe MIME, menghasilkan nama file unik menggunakan UUID, dan
    menyimpannya ke `UPLOAD_FOLDER` yang telah dikonfigurasi.

    Args:
        form_pictures (list[FileStorage]): Daftar objek file (`FileStorage`)
            dari formulir Flask-WTF.

    Returns:
        list[str]: Daftar nama file unik yang berhasil disimpan di server.

    Raises:
        ValueError: Jika salah satu file yang diunggah bukan gambar dengan
                    tipe MIME yang diizinkan ('image/jpeg', 'image/png', 'image/gif').
    """
    saved_filenames = []

    # Mendefinisikan tipe MIME yang diizinkan untuk mencegah unggahan file berbahaya
    allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']

    # Menginisialisasi pustaka python-magic untuk mendeteksi tipe file dari kontennya
    mime_checker = magic.Magic(mime=True)

    # Melakukan iterasi pada setiap file yang diunggah
    for picture in form_pictures:
        # Langkah 1: Validasi Konten File (MIME Type) untuk keamanan.
        # Membaca beberapa byte pertama dari file untuk mendeteksi tipe aslinya.
        file_head = picture.stream.read(2048)
        # Mengembalikan pointer stream ke awal file setelah membaca.
        picture.stream.seek(0)

        # Mendeteksi tipe MIME dari buffer (konten file)
        detected_mime = mime_checker.from_buffer(file_head)

        # Memeriksa apakah tipe MIME yang terdeteksi ada dalam daftar yang diizinkan
        if detected_mime not in allowed_mimes:
            raise ValueError(f'Tipe file tidak valid: terdeteksi {detected_mime}. Hanya gambar yang diizinkan.')
        
        # Langkah 2: Proses Penyimpanan File yang Aman.
        # Mendapatkan ekstensi file asli
        _, f_ext = os.path.splitext(picture.filename)
        # Menghasilkan nama file acak menggunakan UUID untuk mencegah tabrakan nama dan tebakan nama file
        picture_fn = str(uuid.uuid4()) + f_ext

        # Menggabungkan path folder upload dengan nama file baru yang aman
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

        # Menyimpan file ke path yang telah ditentukan
        picture.save(picture_path)
        # Menambahkan nama file yang baru ke dalam daftar untuk dikembalikan
        saved_filenames.append(picture_fn)

    return saved_filenames
