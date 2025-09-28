from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """
    Model pengguna untuk sistem autentikasi dan manajemen akun di Lelana.id.

    Menyimpan data dasar pengguna, termasuk kredensial keamanan dan peran akses.
    Mendukung relasi satu-ke-banyak dengan ulasan (Review) dan itinerari
    perjalanan (Itinerari). Menggunakan Flask-Login melalui UserMixin untuk
    integrasi sesi pengguna.

    Atribut:
        id (int): Primary key unik.
        username (str): Nama pengguna unik (4–25 karakter, diindeks).
        email (str): Email unik dan terverifikasi (diindeks).
        password_hash (str): Hash dari password asli (tidak disimpan dalam bentuk plain text).
        role (str): Peran pengguna; nilai default 'user', bisa diubah menjadi 'admin'.

    Relasi:
        reviews (dynamic relationship): Daftar ulasan yang dibuat pengguna.
        itinerari (dynamic relationship): Daftar itinerari yang dibuat pengguna.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default='user', nullable=False) # Bisa 'user' atau 'admin'

    # Relasi ke Review: Satu user bisa punya banyak review
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    # Relasi ke Itinerari: Satu user bisa membuat banyak itinerari
    itinerari = db.relationship('Itinerari', backref='penulis', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def password(self):
        """
        Mencegah akses langsung ke atribut password dalam bentuk teks biasa.

        Properti ini bersifat read-only dan sengaja memicu AttributeError
        jika ada upaya membaca nilai password, sebagai praktik keamanan
        untuk mencegah kebocoran kredensial.

        Raises:
            AttributeError: Selalu dilempar saat properti ini diakses.
        """
        raise AttributeError('Password bukan atribut yang bisa dibaca')
    
    @password.setter
    def password(self, password):
        """
        Menyimpan password dalam bentuk hash aman menggunakan Werkzeug.

        Dipanggil saat objek User diberi nilai pada atribut `password`.
        Nilai asli tidak pernah disimpan; hanya representasi hash-nya
        yang direkam di kolom `password_hash`.

        Args:
            password (str): Password dalam bentuk teks biasa dari pengguna.
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        Memverifikasi kecocokan password input dengan hash yang tersimpan.

        Digunakan selama proses login untuk memastikan kredensial valid.
        Tidak mengungkapkan informasi tentang struktur hash atau keberadaan akun.

        Args:
            password (str): Password yang dimasukkan pengguna saat login.

        Returns:
            bool: True jika password cocok, False jika tidak.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        Menyediakan representasi string informatif untuk debugging dan logging.

        Format: <User username>

        Returns:
            str: Representasi objek User yang mudah dibaca oleh developer.
        """
        return f'<User {self.username}>'