from app import db

class FotoUlasan(db.Model):
    """Model untuk menyimpan metadata file foto yang terkait dengan ulasan pengguna.

    Setiap entri merepresentasikan satu file gambar yang diunggah sebagai bagian
    dari ulasan wisata atau acara. Foto ini selalu dikaitkan dengan satu ulasan
    melalui relasi foreign key.

    Attributes:
        id (int): Identifier unik foto ulasan (primary key).
        nama_file (str): Nama file foto; maksimal 100 karakter; wajib diisi.
        review_id (int): ID ulasan terkait; merujuk ke tabel 'reviews'; wajib diisi.
    """
    __tablename__ = 'foto_ulasan'

    id = db.Column(db.Integer, primary_key=True)
    nama_file = db.Column(db.String(100), nullable=False)

    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)

    def __repr__(self):
        """Mengembalikan representasi string dari objek FotoUlasan untuk debugging.

        Returns:
            str: Representasi string berformat '<FotoUlasan {nama_file}>'.
        """
        return f'<FotoUlasan {self.nama_file}>'