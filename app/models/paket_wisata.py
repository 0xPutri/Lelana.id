from app import db
from datetime import datetime, timezone

# Association Table untuk relasi Many-to-Many antara PaketWisata dan Wisata
paket_wisata_association = db.Table('paket_wisata_association',
    db.Column('paket_id', db.Integer, db.ForeignKey('paket_wisata.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class PaketWisata(db.Model):
    """Model untuk merepresentasikan paket wisata yang ditawarkan dalam sistem.

    Paket wisata mencakup nama, deskripsi, harga, serta daftar destinasi wisata
    yang termasuk di dalamnya melalui relasi many-to-many. Dapat ditandai sebagai
    dipromosikan untuk ditampilkan secara khusus di antarmuka pengguna.

    Attributes:
        id (int): Identifier unik paket wisata (primary key).
        nama (str): Nama paket wisata; maksimal 150 karakter; wajib diisi.
        deskripsi (str): Deskripsi lengkap paket; wajib diisi.
        harga (int): Harga paket dalam satuan rupiah; wajib diisi.
        is_promoted (bool): Status promosi; jika True, paket ditampilkan sebagai unggulan.
        tanggal_dibuat (datetime): Waktu pembuatan entri; otomatis diisi dengan UTC saat objek dibuat.
        destinasi (list[Wisata]): Daftar objek Wisata yang termasuk dalam paket ini.
    """
    __tablename__ = 'paket_wisata'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.Integer, nullable=False)

    is_promoted = db.Column(db.Boolean, default=False, nullable=False)

    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Mendefinisikan relasi many-to-many ke model Wisata
    destinasi = db.relationship('Wisata', secondary=paket_wisata_association, 
                                lazy='subquery', 
                                backref=db.backref('paket_termasuk', lazy=True))

    def __repr__(self):
        """Mengembalikan representasi string dari objek PaketWisata untuk debugging.

        Returns:
            str: Representasi string berformat '<PaketWisata {nama}>'.
        """
        return f'<PaketWisata {self.nama}>'