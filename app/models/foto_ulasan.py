from app import db

class FotoUlasan(db.Model):
    """
    Model penyimpanan metadata foto yang diunggah sebagai lampiran ulasan.

    Menyimpan nama file unik dari foto yang diunggah pengguna saat memberikan
    ulasan destinasi wisata. File fisik disimpan di direktori upload, sedangkan
    entri ini hanya mencatat referensi nama file dan kaitannya dengan ulasan
    terkait. Memungkinkan satu ulasan memiliki banyak foto.

    Atribut:
        id (int): Primary key unik.
        nama_file (str): Nama file unik (misal: a1b2c3d4.jpg) yang disimpan di server.

    Foreign Key:
        review_id (int): ID ulasan yang memiliki foto ini (merujuk ke tabel 'reviews').

    Catatan:
        File asli disimpan di folder `app/static/uploads/`, sehingga path lengkap
        dapat dibentuk dengan menggabungkan konfigurasi UPLOAD_FOLDER dan nama_file.
    """
    __tablename__ = 'foto_ulasan'

    id = db.Column(db.Integer, primary_key=True)
    nama_file = db.Column(db.String(100), nullable=False)

    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)

    def __repr__(self):
        """
        Menyediakan representasi string informatif untuk debugging dan logging.

        Format: <FotoUlasan nama_file>

        Returns:
            str: Representasi objek FotoUlasan berdasarkan nama file yang disimpan.
        """
        return f'<FotoUlasan {self.nama_file}>'