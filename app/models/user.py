from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class User(UserMixin, db.Model):
    """Model untuk representasi pengguna dalam sistem.

    Kelas ini mendefinisikan atribut, relasi, dan metode terkait pengguna,
    termasuk autentikasi, manajemen token (konfirmasi, reset password),
    dan peran (role).

    Attributes:
        id (int): Primary key unik untuk setiap pengguna.
        username (str): Nama pengguna yang unik.
        email (str): Alamat email pengguna yang unik.
        password_hash (str): Hash dari password pengguna.
        role (str): Peran pengguna, default 'user'. Bisa 'user' atau 'admin'.
        is_confirmed (bool): Status konfirmasi email pengguna, default False.
        reviews (relationship): Relasi ke ulasan yang dibuat oleh pengguna.
        itinerari (relationship): Relasi ke itinerari yang dibuat oleh pengguna.
    """
    __tablename__ = 'users'

    # Mendefinisikan kolom-kolom pada tabel 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default='user', nullable=False)

    # Kolom untuk menandai apakah pengguna telah mengonfirmasi emailnya
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Relasi one-to-many ke model Review
    # 'lazy'='dynamic' berarti query tidak langsung dieksekusi
    # 'cascade' akan menghapus semua review dari user ini jika user dihapus
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    # Relasi one-to-many ke model Itinerari
    itinerari = db.relationship('Itinerari', backref='penulis', lazy='dynamic', cascade="all, delete-orphan")

    def generate_confirmation_token(self):
        """Membuat token konfirmasi email yang aman dan berbatas waktu.

        Token ini berisi ID pengguna yang ditandatangani secara digital.

        Returns:
            str: Token konfirmasi dalam format string.
        """
        # Membuat serializer dengan secret key aplikasi
        s = Serializer(current_app.config['SECRET_KEY'])
        # Menghasilkan token yang berisi ID pengguna
        return s.dumps({'confirm': self.id})
    
    @staticmethod
    def confirm(token, expiration=3600):
        """Memverifikasi token konfirmasi dan mengaktifkan akun pengguna.

        Args:
            token (str): Token konfirmasi yang diterima dari pengguna.
            expiration (int): Masa berlaku token dalam detik (default: 1 jam).

        Returns:
            User | None: Objek pengguna jika konfirmasi berhasil, atau None jika gagal.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Memuat token dan memeriksa masa berlakunya
            data = s.loads(token, max_age=expiration)
        except:
            # Gagal jika token tidak valid atau kedaluwarsa
            return None
        # Mengambil pengguna berdasarkan ID dari data token
        user = User.query.get(data.get('confirm'))
        if user:
            # Mengubah status konfirmasi dan menyimpan ke database
            user.is_confirmed = True
            db.session.add(user)
        return user
    
    def generate_reset_token(self):
        """Membuat token reset password yang aman dan berbatas waktu.

        Returns:
            str: Token reset password dalam format string.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        # Menghasilkan token yang berisi ID pengguna untuk proses reset
        return s.dumps({'reset': self.id})
    
    @staticmethod
    def verify_reset_token(token, expiration=3600):
        """Memverifikasi token reset password dan mengembalikan pengguna terkait.

        Args:
            token (str): Token reset password yang diterima.
            expiration (int): Masa berlaku token dalam detik (default: 1 jam).

        Returns:
            User | None: Objek pengguna jika token valid, atau None jika tidak.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Memuat token dan memeriksa masa berlakunya
            data = s.loads(token, max_age=expiration)
            user_id = data.get('reset')
            # Mengambil pengguna dari database menggunakan ID dari token
            return db.session.get(User, user_id)
        except:
            # Gagal jika token tidak valid atau kedaluwarsa
            return None

    @property
    def password(self):
        """Mencegah akses baca langsung ke atribut password.

        Raises:
            AttributeError: Selalu muncul saat mencoba membaca atribut ini.
        """
        raise AttributeError('Password bukan atribut yang bisa dibaca')
    
    @password.setter
    def password(self, password):
        """Mengatur password pengguna dengan membuat hash-nya.

        Args:
            password (str): Password plaintext yang akan di-hash.
        """
        # Menghasilkan hash dari password dan menyimpannya
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Memverifikasi password yang diberikan dengan hash yang tersimpan.

        Args:
            password (str): Password plaintext untuk diverifikasi.

        Returns:
            bool: True jika password cocok, False jika sebaliknya.
        """
        # Membandingkan password dengan hash yang ada di database
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Mengembalikan representasi string dari objek User untuk debugging.

        Returns:
            str: Representasi string dari objek.
        """
        return f'<User {self.username}>'
