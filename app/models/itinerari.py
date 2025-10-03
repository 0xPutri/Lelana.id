from app import db
from datetime import datetime, timezone

itinerari_wisata_association = db.Table('itinerari_wisata_association',
    db.Column('itinerari_id', db.Integer, db.ForeignKey('itinerari.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class Itinerari(db.Model):
    """Model untuk menyimpan rencana perjalanan (itinerari) yang dibuat pengguna.

    Itinerari berisi judul, deskripsi opsional, dan daftar tempat wisata yang
    dikaitkan melalui relasi many-to-many. Setiap itinerari dimiliki oleh satu
    pengguna.

    Attributes:
        id (int): Identifier unik itinerari (primary key).
        judul (str): Judul itinerari; maksimal 150 karakter; wajib diisi.
        deskripsi (str or None): Deskripsi detail itinerari; opsional.
        tanggal_dibuat (datetime): Waktu pembuatan entri; otomatis diisi dengan UTC saat objek dibuat.
        user_id (int): ID pengguna pemilik itinerari; merujuk ke tabel 'users'; wajib diisi.
        wisata_termasuk (list[Wisata]): Daftar objek Wisata yang termasuk dalam itinerari ini.
    """
    __tablename__ = 'itinerari'

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(150), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    tanggal_dibuat = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key untuk relasi ke tabel User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    wisata_termasuk = db.relationship('Wisata', secondary=itinerari_wisata_association, 
                                      lazy='subquery', 
                                      backref=db.backref('termasuk_dalam_itinerari', lazy=True))

    def __repr__(self):
        """Mengembalikan representasi string dari objek Itinerari untuk debugging.

        Returns:
            str: Representasi string berformat '<Itinerari {judul}>'.
        """
        return f'<Itinerari {self.judul}>'