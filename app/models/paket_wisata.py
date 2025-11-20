from app import db
from datetime import datetime, timezone

# Tabel asosiasi untuk relasi many-to-many antara PaketWisata dan Wisata
paket_wisata_association = db.Table('paket_wisata_association',
    db.Column('paket_id', db.Integer, db.ForeignKey('paket_wisata.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class PaketWisata(db.Model):
    """Model untuk merepresentasikan paket wisata yang ditawarkan.

    Setiap paket memiliki nama, deskripsi, harga, dan dapat mencakup beberapa
    destinasi wisata melalui relasi many-to-many.

    Attributes:
        id (int): Primary key unik untuk setiap paket wisata.
        nama (str): Nama dari paket wisata.
        deskripsi (str): Deskripsi lengkap mengenai paket wisata.
        harga (int): Harga paket wisata.
        is_promoted (bool): Menandakan apakah paket sedang dipromosikan.
        tanggal_dibuat (datetime): Timestamp saat entri dibuat (UTC).
        destinasi (relationship): Relasi many-to-many ke objek Wisata.
    """
    __tablename__ = 'paket_wisata'

    # Mendefinisikan kolom-kolom pada tabel 'paket_wisata'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.Integer, nullable=False)

    # Kolom boolean untuk menandai paket sebagai promosi atau unggulan
    is_promoted = db.Column(db.Boolean, default=False, nullable=False)

    # Kolom untuk mencatat waktu pembuatan, default ke waktu UTC saat ini
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relasi many-to-many ke model Wisata melalui tabel asosiasi
    # 'lazy'='subquery' memuat semua destinasi terkait dalam satu query tambahan
    # 'backref' membuat relasi balik dari Wisata ke PaketWisata
    destinasi = db.relationship('Wisata', secondary=paket_wisata_association, 
                                lazy='subquery', 
                                backref=db.backref('paket_termasuk', lazy=True))

    def __repr__(self):
        """Mengembalikan representasi string dari objek PaketWisata untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<PaketWisata {self.nama}>'
