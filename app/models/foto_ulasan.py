from app import db

class FotoUlasan(db.Model):
    """Model untuk menyimpan path file foto yang terkait dengan sebuah ulasan.

    Setiap entri dalam tabel ini merepresentasikan satu file gambar yang
    diunggah sebagai bagian dari ulasan (review).

    Attributes:
        id (int): Primary key unik untuk setiap foto.
        nama_file (str): Nama file gambar yang disimpan di server.
        review_id (int): Foreign key yang menunjuk ke ulasan induknya.
    """
    __tablename__ = 'foto_ulasan'

    # Mendefinisikan kolom-kolom pada tabel 'foto_ulasan'
    id = db.Column(db.Integer, primary_key=True)
    # Kolom untuk menyimpan nama file unik dari gambar yang diunggah
    nama_file = db.Column(db.String(100), nullable=False)

    # Foreign Key yang menghubungkan foto ini ke sebuah review spesifik
    # Setiap foto harus terkait dengan satu review
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)

    def __repr__(self):
        """Mengembalikan representasi string dari objek FotoUlasan untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<FotoUlasan {self.nama_file}>'
