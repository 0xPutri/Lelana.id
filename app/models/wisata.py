from app import db
from datetime import datetime, timezone

class Wisata(db.Model):
    """Model untuk merepresentasikan tempat wisata dalam sistem.

    Menyimpan informasi lengkap tentang destinasi wisata, termasuk lokasi geografis,
    kategori, deskripsi, dan tautan gambar. Tempat wisata dapat dikaitkan dengan
    banyak ulasan dari pengguna.

    Attributes:
        id (int): Identifier unik tempat wisata (primary key).
        nama (str): Nama tempat wisata; maksimal 100 karakter; wajib diisi.
        kategori (str): Kategori wisata (misalnya alam, budaya, kuliner); maksimal 50 karakter; wajib diisi.
        lokasi (str): Alamat atau deskripsi lokasi; maksimal 200 karakter; wajib diisi.
        deskripsi (str): Deskripsi lengkap tempat wisata; wajib diisi.
        gambar_url (str or None): URL gambar utama tempat wisata; opsional; maksimal 255 karakter.
        latitude (float or None): Koordinat lintang lokasi; opsional.
        longitude (float or None): Koordinat bujur lokasi; opsional.
        tanggal_dibuat (datetime): Waktu pembuatan entri; otomatis diisi dengan UTC saat objek dibuat.
        reviews (list[Review]): Daftar ulasan yang diberikan untuk tempat wisata ini.
        events (list[Event]): Daftar acara yang terkait dengan tempat wisata ini.
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

    # Relasi ke Event: Satu wisata bisa punya banyak event
    events = db.relationship('Event', backref='wisata', lazy='dynamic')

    def __repr__(self):
        """Mengembalikan representasi string dari objek Wisata untuk debugging.

        Returns:
            str: Representasi string berformat '<Wisata {nama}>'.
        """
        return f'<Wisata {self.nama}>'