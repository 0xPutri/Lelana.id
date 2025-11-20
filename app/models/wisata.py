from app import db
from datetime import datetime, timezone

class Wisata(db.Model):
    """Model untuk merepresentasikan data tempat wisata.

    Kelas ini mendefinisikan struktur tabel 'wisata', menyimpan informasi
    detail tentang destinasi termasuk lokasi, deskripsi, dan relasi ke ulasan.

    Attributes:
        id (int): Primary key unik untuk setiap tempat wisata.
        nama (str): Nama tempat wisata.
        kategori (str): Kategori wisata (misal: 'Alam', 'Budaya').
        lokasi (str): Alamat atau deskripsi lokasi.
        deskripsi (str): Deskripsi lengkap mengenai tempat wisata.
        gambar_url (str | None): URL ke gambar utama (opsional).
        latitude (float | None): Koordinat lintang untuk pemetaan (opsional).
        longitude (float | None): Koordinat bujur untuk pemetaan (opsional).
        tanggal_dibuat (datetime): Timestamp saat entri dibuat (UTC).
        reviews (relationship): Relasi one-to-many ke ulasan terkait.
        events (relationship): Relasi one-to-many ke acara terkait.
    """
    __tablename__ = 'wisata'

    # Mendefinisikan kolom-kolom pada tabel 'wisata'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False, index=True)
    kategori = db.Column(db.String(50), nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    gambar_url = db.Column(db.String(255), nullable=True)

    # Kolom opsional untuk menyimpan koordinat geografis
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Kolom untuk mencatat waktu pembuatan, default ke waktu UTC saat ini
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relasi one-to-many ke model Review
    # 'lazy'='dynamic' memungkinkan query lebih lanjut pada hasil relasi
    # 'cascade' akan menghapus semua review jika wisata ini dihapus
    reviews = db.relationship('Review', backref='wisata_reviewed', lazy='dynamic', cascade="all, delete-orphan")

    # Relasi one-to-many ke model Event
    events = db.relationship('Event', backref='wisata', lazy='dynamic')

    def __repr__(self):
        """Mengembalikan representasi string dari objek Wisata untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<Wisata {self.nama}>'
