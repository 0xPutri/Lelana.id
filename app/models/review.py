from app import db
from datetime import datetime, timezone

class Review(db.Model):
    """Model untuk menyimpan ulasan pengguna terhadap tempat wisata.

    Setiap ulasan memiliki rating, komentar, dan terhubung dengan satu pengguna
    serta satu tempat wisata. Ulasan juga dapat memiliki beberapa foto terkait.

    Attributes:
        id (int): Primary key unik untuk setiap ulasan.
        rating (int): Nilai rating dari 1 hingga 5.
        komentar (str): Isi teks dari ulasan.
        tanggal_dibuat (datetime): Timestamp saat ulasan dibuat (UTC).
        user_id (int): Foreign key yang menunjuk ke pengguna yang menulis ulasan.
        wisata_id (int): Foreign key yang menunjuk ke tempat wisata yang diulas.
        foto (relationship): Relasi one-to-many ke objek FotoUlasan.
    """
    __tablename__ = 'reviews'

    # Mendefinisikan kolom-kolom pada tabel 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # Rating dari 1 sampai 5
    komentar = db.Column(db.Text, nullable=False)
    # Kolom untuk mencatat waktu pembuatan, default ke waktu UTC saat ini
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key yang menghubungkan ulasan ke pembuatnya (pengguna)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Foreign Key yang menghubungkan ulasan ke tempat wisata yang diulas
    wisata_id = db.Column(db.Integer, db.ForeignKey('wisata.id'), nullable=False)

    # Relasi one-to-many ke model FotoUlasan
    # 'cascade' akan menghapus semua foto terkait jika ulasan ini dihapus
    foto = db.relationship('FotoUlasan', backref='review', cascade="all, delete-orphan")

    def __repr__(self):
        """Mengembalikan representasi string dari objek Review untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<Review {self.id} oleh User {self.user_id}>'
