import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, IntegerField, FloatField, widgets, MultipleFileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from .models.user import User
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from .models.wisata import Wisata

class RegistrationForm(FlaskForm):
    """Formulir pendaftaran pengguna baru dengan validasi lengkap.

    Memastikan username dan email unik, serta menerapkan kebijakan keamanan
    password yang ketat (minimal 6 karakter, kombinasi huruf besar/kecil,
    angka, dan karakter spesial).
    """
    username = StringField('Username', 
                           validators=[DataRequired(message='Username wajib diisi.'), 
                                       Length(min=4, max=25, message='Username harus antara 4 dan 25 karakter.')])
    email = StringField('Email', 
                        validators=[DataRequired(message='Email wajib diisi.'), 
                                    Email(message='Format email tidak valid.')])
    password = PasswordField('Password', 
                             validators=[DataRequired(message='Password wajib diisi.'), 
                                         Length(min=6, message='Password minimal 6 karakter.')])
    confirm_password = PasswordField('Konfirmasi Password', 
                                     validators=[DataRequired(message='Konfirmasi password wajib diisi.'), 
                                                 EqualTo('password', message='Password tidak cocok.')])
    submit = SubmitField('Daftar')

    def validate_password(self, password):
        """Memvalidasi kekuatan password berdasarkan kebijakan keamanan.

        Password harus mengandung setidaknya:
        - Satu huruf kecil
        - Satu huruf besar
        - Satu angka
        - Satu karakter spesial dari himpunan @$!%*?&#

        Args:
            password (PasswordField): Field password dari formulir.

        Raises:
            ValidationError: Jika salah satu kriteria keamanan tidak terpenuhi.
        """
        p = password.data
        if not re.search(r'[a-z]', p):
            raise ValidationError('Password harus mengandung setidaknya satu huruf kecil.')
        if not re.search(r'[A-Z]', p):
            raise ValidationError('Password harus mengandung setidaknya satu huruf besar.')
        if not re.search(r'\d', p):
            raise ValidationError('Password harus mengandung setidaknya satu angka.')
        if not re.search(r'[@$!%*?&#]', p):
            raise ValidationError('Password harus mengandung setidaknya satu karakter spesial (@$!%*?&#).')

    def validate_username(self, username):
        """Memastikan username belum digunakan oleh pengguna lain.

        Args:
            username (StringField): Field username dari formulir.

        Raises:
            ValidationError: Jika username sudah terdaftar di sistem.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username tersebut sudah digunakan. Silakan pilih yang lain.')
    
    def validate_email(self, email):
        """Memastikan alamat email belum terdaftar di sistem.

        Args:
            email (StringField): Field email dari formulir.

        Raises:
            ValidationError: Jika email sudah digunakan oleh akun lain.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email tersebut sudah terdaftar. Silakan gunakan email lain.')

class LoginForm(FlaskForm):
    """Formulir login pengguna dengan opsi mengingat sesi.

    Memverifikasi keberadaan email dan kecocokan password saat autentikasi.
    """
    email = StringField('Email', 
                        validators=[DataRequired(message='Email wajib diisi.'), 
                                    Email(message='Format email tidak valid.')])
    password = PasswordField('Password', 
                             validators=[DataRequired(message='Password wajib diisi.')])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Login')

class WisataForm(FlaskForm):
    """Formulir untuk menambahkan atau mengedit tempat wisata.

    Mengumpulkan informasi dasar destinasi wisata, termasuk koordinat geografis
    opsional dan URL gambar.
    """
    nama = StringField('Nama Wisata', 
                       validators=[DataRequired(message='Nama wisata wajib diisi.')])
    kategori = StringField('Kategori', 
                           validators=[DataRequired(message='Kategori wajib diisi.')])
    lokasi = StringField('Lokasi (Alamat/Koordinat)', 
                         validators=[DataRequired(message='Lokasi wajib diisi.')])
    deskripsi = TextAreaField('Deskripsi', 
                              validators=[DataRequired(message='Deskripsi wajib diisi.')])
    gambar_url = StringField('URL Gambar (Opsional)')

    latitude = FloatField('Latitude (Contoh: -7.421... Opsional)',
                          validators=[Optional()])
    longitude = FloatField('Longitude (Contoh: 109.243 Opsional)',
                           validators=[Optional()])

    submit = SubmitField('Simpan')

class EventForm(FlaskForm):
    """Formulir untuk membuat atau memperbarui acara (event).

    Mengelola detail acara seperti nama, tanggal, lokasi, deskripsi,
    dan penyelenggara (opsional).
    """
    nama = StringField('Nama Event', 
                       validators=[DataRequired(message='Nama event wajib diisi.')])
    tanggal = DateField('Tanggal Pelaksanaan', format='%Y-%m-%d', 
                        validators=[DataRequired(message='Tanggal wajib diisi.')])
    lokasi = StringField('Lokasi Event', 
                         validators=[DataRequired(message='Lokasi wajib diisi.')])
    deskripsi = TextAreaField('Deskripsi', 
                              validators=[DataRequired(message='Deskripsi wajib diisi.')])
    penyelenggara = StringField('Penyelenggara (Opsional)')
    submit = SubmitField('Simpan Event')

class ReviewForm(FlaskForm):
    """Formulir untuk memberikan ulasan terhadap tempat wisata.

    Memungkinkan pengguna memberikan rating (1–5), komentar teks,
    dan mengunggah beberapa foto ulasan.
    """
    rating = IntegerField('Rating (1-5)', 
                          validators=[DataRequired(), NumberRange(min=1, max=5, message='Rating harus antara 1 dan 5.')])
    komentar = TextAreaField('Komentar Anda', 
                             validators=[DataRequired(message='Komentar tidak boleh kosong.')])
    foto = MultipleFileField('Unggah Foto (Opsional)', 
                             validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Hanya gambar (jpg, png, jpeg) yang diizinkan!')])
    submit = SubmitField('Kirim Review')

def get_all_wisata():
    """Mengambil semua tempat wisata yang tersedia, diurutkan berdasarkan nama.

    Digunakan sebagai query factory untuk field seleksi wisata di formulir
    paket wisata dan itinerari.

    Returns:
        list[Wisata]: Daftar objek Wisata yang diurutkan secara alfabetis.
    """
    return Wisata.query.order_by(Wisata.nama).all()

class PaketWisataForm(FlaskForm):
    """Formulir untuk membuat atau mengelola paket wisata.

    Memungkinkan admin menentukan nama, deskripsi, harga, destinasi yang
    termasuk dalam paket, serta status promosi.
    """
    nama = StringField('Nama Paket Wisata', 
                       validators=[DataRequired(message='Nama paket wajib diisi.')])
    deskripsi = TextAreaField('Deskripsi Paket', 
                              validators=[DataRequired(message='Deskripsi paket wajib diisi.')])
    harga = IntegerField('Harga (Rp)', 
                         validators=[DataRequired(message='Harga wajib diisi.')])

    destinasi = QuerySelectMultipleField(
        'Pilih Destinasi yang Termasuk dalam Paket',
        query_factory=get_all_wisata,
        get_label='nama',
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    is_promoted = BooleanField('Tandai sebagai Paket Promosi/Endorsment')

    submit = SubmitField('Simpan Paket Wisata')

class ItinerariForm(FlaskForm):
    """Formulir untuk membuat rencana perjalanan (itinerari) pengguna.

    Memungkinkan pemilihan beberapa tempat wisata dari daftar yang tersedia
    dan penambahan deskripsi opsional.
    """
    judul = StringField('Judul Itinerari', 
                        validators=[DataRequired(message='Judul wajib diisi.')])
    deskripsi = TextAreaField('Cerita atau Deskripsi Singkat (Opsional)')

    wisata_termasuk = QuerySelectMultipleField(
        'Pilih Tempat Wisata untuk Dimasukkan',
        query_factory=get_all_wisata,
        get_label='nama',
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    submit = SubmitField('Simpan Itinerari')

class AdminEditUserForm(FlaskForm):
    """Formulir untuk admin mengedit profil pengguna lain.

    Memungkinkan perubahan username, email, dan peran (role) dengan validasi
    untuk memastikan keunikan username dan email.
    """
    username = StringField('Username', 
                           validators=[DataRequired(message='Username wajib diisi.'),
                                       Length(min=4, max=25)])
    email = StringField('Email', 
                        validators=[DataRequired(message='Email wajib diisi.'),
                                    Email(message='Format email tidak valid.')])
    role = SelectField('Peran (Role)', 
                       choices=[('user', 'User'), ('admin', 'Admin')],
                                validators=[DataRequired()])
    submit = SubmitField('Simpan Perubahan')

    def __init__(self, original_user, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_username(self, username):
        """Memvalidasi keunikan username hanya jika diubah.

        Args:
            username (StringField): Field username dari formulir.

        Raises:
            ValidationError: Jika username baru sudah digunakan oleh pengguna lain.
        """
        if username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username tersebut sudah digunakan.')

    def validate_email(self, email):
        """Memvalidasi keunikan email hanya jika diubah.

        Args:
            email (StringField): Field email dari formulir.

        Raises:
            ValidationError: Jika email baru sudah terdaftar oleh akun lain.
        """
        if email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email tersebut sudah terdaftar.')