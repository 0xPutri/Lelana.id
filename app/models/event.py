from app import db
from datetime import datetime, timezone

class Event(db.Model):
    """Model untuk representasi data acara atau event.

    Kelas ini mendefinisikan struktur tabel 'event' di database, termasuk
    detail acara seperti nama, tanggal, lokasi, dan deskripsi.

    Attributes:
        id (int): Primary key unik untuk setiap event.
        nama (str): Nama acara.
        tanggal (datetime): Tanggal dan waktu pelaksanaan acara.
        lokasi (str): Lokasi tempat acara diselenggarakan.
        deskripsi (str): Deskripsi lengkap mengenai acara.
        penyelenggara (str | None): Nama penyelenggara acara (opsional).
        tanggal_dibuat (datetime): Timestamp saat entri dibuat (UTC).
        id_wisata (int | None): Foreign key opsional ke tabel 'wisata'.
    """
    __tablename__ = 'event'

    # Mendefinisikan kolom-kolom pada tabel 'event'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    tanggal = db.Column(db.DateTime, nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    penyelenggara = db.Column(db.String(100))
    
    # Kolom untuk mencatat waktu pembuatan, default ke waktu UTC saat ini
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key untuk relasi opsional ke tabel Wisata
    # Sebuah event bisa terkait dengan satu lokasi wisata tertentu
    id_wisata = db.Column(db.Integer, db.ForeignKey('wisata.id'), nullable=True, index=True)

    def __repr__(self):
        """Mengembalikan representasi string dari objek Event untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<Event {self.nama}>'
