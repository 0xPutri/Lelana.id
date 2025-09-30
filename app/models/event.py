from app import db
from datetime import datetime, timezone

class Event(db.Model):
    """
    Model acara atau event budaya lokal di wilayah Banyumas dan sekitarnya.

    Menyimpan informasi lengkap tentang kegiatan seperti festival, pertunjukan,
    atau perayaan adat, termasuk tanggal pelaksanaan, lokasi, deskripsi, dan
    pihak penyelenggara (opsional). Digunakan untuk mempromosikan kekayaan
    budaya lokal melalui platform Lelana.id.

    Atribut:
        id (int): Primary key unik.
        nama (str): Nama event (diindeks untuk pencarian dan pengurutan).
        tanggal (datetime): Waktu pelaksanaan event (wajib, dalam format lengkap).
        lokasi (str): Tempat penyelenggaraan event (alamat atau nama tempat).
        deskripsi (str): Informasi detail tentang acara, tujuan, dan aktivitas.
        penyelenggara (str, optional): Nama komunitas, lembaga, atau individu penyelenggara.
        tanggal_dibuat (datetime): Waktu entri dibuat di sistem (default: UTC saat ini).
    """
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    tanggal = db.Column(db.DateTime, nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    penyelenggara = db.Column(db.String(100))
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """
        Menyediakan representasi string singkat untuk debugging dan logging.

        Format: <Event nama_event>

        Returns:
            str: Representasi objek Event yang mencerminkan identitas acara.
        """
        return f'<Event {self.nama}>'