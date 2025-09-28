import uuid
import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_pictures(form_pictures):
    """
    Menyimpan satu atau beberapa file gambar yang diunggah melalui formulir ke direktori upload.

    Setiap file diberi nama unik menggunakan UUID4 untuk mencegah tabrakan nama,
    lalu disimpan di folder yang ditentukan oleh konfigurasi `UPLOAD_FOLDER`.
    Ekstensi file asli dipertahankan, dan nama file di-sanitasi menggunakan
    `secure_filename` untuk keamanan.

    Digunakan terutama saat pengguna mengirim ulasan dengan lampiran foto,
    atau admin mengunggah gambar untuk konten wisata/event.

    Args:
        form_pictures (list[FileStorage]): Daftar objek file dari MultipleFileField
            pada formulir WTForms (misalnya dari ReviewForm).

    Returns:
        list[str]: Daftar nama file yang berhasil disimpan (hanya nama file,
                   bukan path lengkap), siap disimpan ke database.

    Catatan:
        Fungsi ini mengasumsikan bahwa semua file dalam `form_pictures` telah
        lolos validasi ekstensi (misalnya melalui FileAllowed) sebelum diproses.
    """
    saved_filenames = []
    for picture in form_pictures:
        _, f_ext = os.path.splitext(picture.filename)
        picture_fn = str(uuid.uuid4()) + f_ext

        filename = secure_filename(picture_fn)

        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        picture.save(picture_path)
        saved_filenames.append(filename)
    return saved_filenames