from app import db
from datetime import datetime

# Association Table untuk relasi Many-to-Many antara PaketWisata dan Wisata
paket_wisata_association = db.Table('paket_wisata_association',
    db.Column('paket_id', db.Integer, db.ForeignKey('paket_wisata.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class PaketWisata(db.Model):
    """
    Model paket wisata gabungan yang dirancang oleh admin untuk memudahkan
    perencanaan perjalanan pengguna di wilayah Banyumas.

    Setiap paket terdiri dari nama, deskripsi, harga (dalam Rupiah), dan daftar
    destinasi wisata yang dipilih dari katalog yang tersedia. Fitur tambahan
    `is_promoted` memungkinkan admin menandai paket tertentu sebagai unggulan
    untuk ditampilkan di halaman utama atau promosi khusus.

    Atribut:
        id (int): Primary key unik.
        nama (str): Nama paket wisata (diindeks untuk pencarian).
        deskripsi (str): Penjelasan isi dan manfaat paket (wajib).
        harga (int): Harga paket dalam satuan Rupiah (tanpa pemisah ribuan).
        is_promoted (bool): Penanda apakah paket ditampilkan sebagai unggulan (default: False).
        tanggal_dibuat (datetime): Waktu paket dibuat (default: UTC saat ini).

    Relasi:
        destinasi (relationship): Daftar objek Wisata yang termasuk dalam paket,
            menggunakan tabel asosiasi 'paket_wisata_association'.
            Akses balik tersedia melalui atribut 'paket_termasuk' pada model Wisata.
    """
    __tablename__ = 'paket_wisata'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False, index=True)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.Integer, nullable=False)

    is_promoted = db.Column(db.Boolean, default=False, nullable=False)

    tanggal_dibuat = db.Column(db.DateTime, default=datetime.utcnow)

    # Mendefinisikan relasi many-to-many ke model Wisata
    destinasi = db.relationship('Wisata', secondary=paket_wisata_association, 
                                lazy='subquery', 
                                backref=db.backref('paket_termasuk', lazy=True))

    def __repr__(self):
        """
        Menyediakan representasi string singkat untuk debugging dan logging.

        Format: <PaketWisata nama_paket>

        Returns:
            str: Representasi objek PaketWisata yang mudah dibaca oleh developer.
        """
        return f'<PaketWisata {self.nama}>'