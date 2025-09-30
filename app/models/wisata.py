from app import db
from datetime import datetime, timezone

class Wisata(db.Model):
    """
    Model destinasi wisata yang menjadi inti konten Lelana.id.

    Menyimpan informasi lengkap tentang tempat wisata di wilayah Banyumas dan
    sekitarnya, termasuk deskripsi, lokasi, kategori, serta koordinat GPS
    opsional untuk integrasi peta. Setiap entri otomatis dicatat waktu
    pembuatannya.

    Atribut:
        id (int): Primary key unik.
        nama (str): Nama destinasi wisata (diindeks untuk pencarian cepat).
        kategori (str): Jenis wisata (misal: alam, budaya, religi, kuliner).
        lokasi (str): Alamat atau deskripsi lokasi lengkap.
        deskripsi (str): Informasi naratif tentang wisata (wajib).
        gambar_url (str, optional): URL gambar utama dari sumber eksternal.
        latitude (float, optional): Koordinat lintang untuk peta interaktif.
        longitude (float, optional): Koordinat bujur untuk peta interaktif.
        tanggal_dibuat (datetime): Waktu entri dibuat (default: UTC).

    Relasi:
        reviews (dynamic relationship): Daftar ulasan pengguna untuk destinasi ini.
            Menggunakan cascade "delete-orphan" agar ulasan otomatis terhapus
            jika destinasi dihapus.
    """
    __tablename__ = 'wisata'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False, index=True)
    kategori = db.Column(db.String(50), nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    gambar_url = db.Column(db.String(255), nullable=True)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relasi ke Review: Satu wisata bisa punya banyak review
    reviews = db.relationship('Review', backref='wisata_reviewed', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        """
        Menyediakan representasi string singkat untuk debugging dan logging.

        Format: <Wisata nama_wisata>

        Returns:
            str: Representasi objek Wisata yang mudah dibaca oleh developer.
        """
        return f'<Wisata {self.nama}>'