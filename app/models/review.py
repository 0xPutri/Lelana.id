from app import db
from datetime import datetime

class Review(db.Model):
    """
    Model ulasan pengguna terhadap destinasi wisata di Lelana.id.

    Menyimpan rating numerik (1–5), komentar teks, dan referensi ke pengguna
    serta destinasi yang diulas. Setiap ulasan dapat memiliki satu atau beberapa
    foto pendukung melalui relasi ke model FotoUlasan. Waktu pembuatan otomatis
    dicatat dan diindeks untuk pengurutan kronologis.

    Atribut:
        id (int): Primary key unik.
        rating (int): Nilai ulasan antara 1 hingga 5 (wajib).
        komentar (str): Ulasan teks dari pengguna (wajib).
        tanggal_dibuat (datetime): Waktu ulasan dibuat (default: UTC saat ini, diindeks).

    Foreign Key:
        user_id (int): ID pengguna yang memberikan ulasan (merujuk ke tabel 'users').
        wisata_id (int): ID destinasi wisata yang diulas (merujuk ke tabel 'wisata').

    Relasi:
        foto (dynamic relationship): Daftar foto yang diunggah bersama ulasan ini.
            Menggunakan cascade "delete-orphan" agar foto otomatis terhapus
            jika ulasan dihapus.
    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # Rating dari 1 sampai 5
    komentar = db.Column(db.Text, nullable=False)
    tanggal_dibuat = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wisata_id = db.Column(db.Integer, db.ForeignKey('wisata.id'), nullable=False)

    foto = db.relationship('FotoUlasan', backref='review', cascade="all, delete-orphan")

    def __repr__(self):
        """
        Menyediakan representasi string informatif untuk debugging dan logging.

        Format: <Review id oleh User user_id>

        Returns:
            str: Representasi objek Review yang mencakup ID ulasan dan ID pengguna.
        """
        return f'<Review {self.id} oleh User {self.user_id}>'