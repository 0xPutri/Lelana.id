from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class User(UserMixin, db.Model):
    """Model pengguna sistem yang mendukung autentikasi, otorisasi, dan manajemen akun.

    Pengguna dapat memiliki peran 'user' atau 'admin', memberikan ulasan, membuat
    itinerari, serta menjalani proses konfirmasi email. Password disimpan dalam
    bentuk hash untuk keamanan.

    Attributes:
        id (int): Identifier unik pengguna (primary key).
        username (str): Nama pengguna; unik; maksimal 64 karakter; wajib diisi.
        email (str): Alamat email; unik; maksimal 120 karakter; wajib diisi.
        password_hash (str): Hash dari password pengguna; disimpan secara aman.
        role (str): Peran pengguna; nilai default 'user'; bisa berupa 'user' atau 'admin'.
        is_confirmed (bool): Status konfirmasi email; default False.
        reviews (list[Review]): Daftar ulasan yang dibuat pengguna ini.
        itinerari (list[Itinerari]): Daftar itinerari yang dibuat pengguna ini.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default='user', nullable=False) # Bisa 'user' atau 'admin'

    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relasi ke Review: Satu user bisa punya banyak review
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    # Relasi ke Itinerari: Satu user bisa membuat banyak itinerari
    itinerari = db.relationship('Itinerari', backref='penulis', lazy='dynamic', cascade="all, delete-orphan")

    def generate_confirmation_token(self):
        """Membuat token konfirmasi email berbasis waktu untuk pengguna ini.

        Token dihasilkan menggunakan SECRET_KEY aplikasi dan berisi ID pengguna.
        Token ini digunakan dalam proses verifikasi alamat email.

        Returns:
            str: Token konfirmasi yang dapat dikirim melalui email.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})
    
    @staticmethod
    def confirm(token, expiration=3600):
        """Memverifikasi token konfirmasi dan menandai pengguna sebagai terkonfirmasi.

        Token yang kedaluwarsa atau tidak valid akan menghasilkan nilai None.
        Jika token valid dan pengguna ditemukan, status `is_confirmed` diubah menjadi True.

        Args:
            token (str): Token konfirmasi yang diterima dari pengguna.
            expiration (int): Masa berlaku token dalam detik (default: 3600 detik = 1 jam).

        Returns:
            User or None: Objek pengguna jika konfirmasi berhasil; None jika gagal.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return None
        user = User.query.get(data.get('confirm'))
        if user:
            user.is_confirmed = True
            db.session.add(user)
        return user

    @property
    def password(self):
        """Mencegah akses langsung ke atribut password.

        Raises:
            AttributeError: Selalu memunculkan error karena password tidak boleh dibaca.
        """
        raise AttributeError('Password bukan atribut yang bisa dibaca')
    
    @password.setter
    def password(self, password):
        """Mengatur password pengguna dengan menyimpan hash-nya.

        Password asli tidak pernah disimpan; hanya representasi hash yang disimpan
        di database untuk keamanan.

        Args:
            password (str): Password plaintext yang akan di-hash dan disimpan.
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Memverifikasi apakah password yang diberikan cocok dengan hash yang tersimpan.

        Args:
            password (str): Password plaintext untuk diverifikasi.

        Returns:
            bool: True jika password cocok; False jika tidak.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Mengembalikan representasi string dari objek User untuk debugging.

        Returns:
            str: Representasi string berformat '<User {username}>'.
        """
        return f'<User {self.username}>'