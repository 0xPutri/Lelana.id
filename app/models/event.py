from app import db
from datetime import datetime, timezone

class Event(db.Model):
    """Representasi model Event untuk menyimpan informasi acara dalam sistem.

    Model ini mencakup detail dasar suatu acara seperti nama, tanggal pelaksanaan,
    lokasi, deskripsi, dan penyelenggara. Digunakan untuk manajemen dan
    penjadwalan acara dalam aplikasi pariwisata.

    Attributes:
        id (int): Identifier unik acara (primary key).
        nama (str): Nama acara; maksimal 150 karakter; wajib diisi.
        tanggal (datetime): Tanggal dan waktu pelaksanaan acara; wajib diisi.
        lokasi (str): Lokasi acara; maksimal 200 karakter; wajib diisi.
        deskripsi (str): Deskripsi lengkap acara; wajib diisi.
        penyelenggara (str or None): Nama penyelenggara acara; opsional; maksimal 100 karakter.
        tanggal_dibuat (datetime): Waktu pembuatan entri; otomatis diisi dengan UTC saat objek dibuat.
        id_wisata (int or None): Foreign key yang merujuk ke 'wisata.id'; opsional.
    """
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    tanggal = db.Column(db.DateTime, nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    penyelenggara = db.Column(db.String(100))
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key untuk relasi opsional ke Wisata
    id_wisata = db.Column(db.Integer, db.ForeignKey('wisata.id'), nullable=True, index=True)

    def __repr__(self):
        """Mengembalikan representasi string dari objek Event untuk debugging.

        Returns:
            str: Representasi string berformat '<Event {nama}>'.
        """
        return f'<Event {self.nama}>'