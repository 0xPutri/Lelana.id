from app import db
from datetime import datetime, timezone

# Tabel asosiasi untuk relasi many-to-many antara Itinerari dan Wisata
itinerari_wisata_association = db.Table('itinerari_wisata_association',
    db.Column('itinerari_id', db.Integer, db.ForeignKey('itinerari.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class Itinerari(db.Model):
    """Model untuk menyimpan rencana perjalanan (itinerari) yang dibuat pengguna.

    Setiap itinerari memiliki judul, deskripsi, dan terhubung dengan satu
    pengguna serta beberapa tempat wisata melalui relasi many-to-many.

    Attributes:
        id (int): Primary key unik untuk setiap itinerari.
        judul (str): Judul dari rencana perjalanan.
        deskripsi (str | None): Deskripsi atau catatan tambahan (opsional).
        tanggal_dibuat (datetime): Timestamp saat entri dibuat (UTC).
        user_id (int): Foreign key yang menunjuk ke pengguna yang membuat.
        wisata_termasuk (relationship): Relasi many-to-many ke objek Wisata.
    """
    __tablename__ = 'itinerari'

    # Mendefinisikan kolom-kolom pada tabel 'itinerari'
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(150), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    # Kolom untuk mencatat waktu pembuatan, default ke waktu UTC saat ini
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key yang menghubungkan itinerari ke pembuatnya (pengguna)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relasi many-to-many ke model Wisata melalui tabel asosiasi
    # 'lazy'='subquery' memuat semua wisata terkait dalam satu query tambahan
    # 'backref' membuat relasi balik dari Wisata ke Itinerari
    wisata_termasuk = db.relationship('Wisata', secondary=itinerari_wisata_association, 
                                      lazy='subquery', 
                                      backref=db.backref('termasuk_dalam_itinerari', lazy=True))

    def __repr__(self):
        """Mengembalikan representasi string dari objek Itinerari untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<Itinerari {self.judul}>'
