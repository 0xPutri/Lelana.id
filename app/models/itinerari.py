from app import db
from datetime import datetime, timezone

itinerari_wisata_association = db.Table('itinerari_wisata_association',
    db.Column('itinerari_id', db.Integer, db.ForeignKey('itinerari.id'), primary_key=True),
    db.Column('wisata_id', db.Integer, db.ForeignKey('wisata.id'), primary_key=True)
)

class Itinerari(db.Model):
    """
    Model rencana perjalanan (itinerari) yang dibuat oleh pengguna terautentikasi.

    Memungkinkan pengguna menyusun petualangan pribadi dengan memilih beberapa
    destinasi wisata dari katalog Lelana.id, dilengkapi judul dan deskripsi
    opsional. Setiap itinerari dikaitkan dengan satu pengguna dan dapat mencakup
    banyak destinasi melalui relasi many-to-many.

    Atribut:
        id (int): Primary key unik.
        judul (str): Nama atau tema itinerari (wajib).
        deskripsi (str, optional): Cerita, catatan, atau tips perjalanan.
        tanggal_dibuat (datetime): Waktu pembuatan (diindeks untuk pengurutan).

    Foreign Key:
        user_id (int): ID pengguna pembuat itinerari (merujuk ke tabel 'users').

    Relasi:
        wisata_termasuk (relationship): Daftar objek Wisata yang dipilih dalam itinerari,
            menggunakan tabel asosiasi 'itinerari_wisata_association'.
            Akses balik tersedia di model Wisata melalui atribut 'termasuk_dalam_itinerari'.
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
        """
        Menyediakan representasi string informatif untuk debugging dan logging.

        Format: <Itinerari judul_itinerari>

        Returns:
            str: Representasi objek Itinerari berdasarkan judul yang diberikan pengguna.
        """
        return f'<Itinerari {self.judul}>'