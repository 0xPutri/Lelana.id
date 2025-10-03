from app import db
from datetime import datetime, timezone

class Review(db.Model):
    """Model untuk menyimpan ulasan pengguna terhadap tempat wisata.

    Setiap ulasan mencakup rating numerik (1–5), komentar teks, dan dapat dilengkapi
    dengan satu atau beberapa foto. Ulasan selalu dikaitkan dengan satu pengguna
    dan satu tempat wisata.

    Attributes:
        id (int): Identifier unik ulasan (primary key).
        rating (int): Nilai rating dari 1 hingga 5; wajib diisi.
        komentar (str): Isi ulasan dalam bentuk teks; wajib diisi.
        tanggal_dibuat (datetime): Waktu pembuatan ulasan; otomatis diisi dengan UTC saat objek dibuat.
        user_id (int): ID pengguna yang memberikan ulasan; merujuk ke tabel 'users'; wajib diisi.
        wisata_id (int): ID tempat wisata yang diulas; merujuk ke tabel 'wisata'; wajib diisi.
        foto (list[FotoUlasan]): Daftar foto yang dilampirkan pada ulasan ini.
    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # Rating dari 1 sampai 5
    komentar = db.Column(db.Text, nullable=False)
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wisata_id = db.Column(db.Integer, db.ForeignKey('wisata.id'), nullable=False)

    foto = db.relationship('FotoUlasan', backref='review', cascade="all, delete-orphan")

    def __repr__(self):
        """Mengembalikan representasi string dari objek Review untuk debugging.

        Returns:
            str: Representasi string berformat '<Review {id} oleh User {user_id}>'.
        """
        return f'<Review {self.id} oleh User {self.user_id}>'