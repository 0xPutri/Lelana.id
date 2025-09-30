import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, IntegerField, FloatField, widgets, MultipleFileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from .models.user import User
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from .models.wisata import Wisata

class RegistrationForm(FlaskForm):
    """
    Formulir pendaftaran pengguna baru di Lelana.id.

    Memvalidasi keunikan username dan email terhadap database, serta memastikan
    kekuatan password minimal. Digunakan pada halaman registrasi publik.

    Field:
        username (StringField): Nama pengguna unik (4–25 karakter).
        email (StringField): Alamat email valid.
        password (PasswordField): Kata sandi minimal 6 karakter.
        confirm_password (PasswordField): Konfirmasi kata sandi harus cocok.
        submit (SubmitField): Tombol kirim formulir.
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
        """
        Memvalidasi kekuatan password berdasarkan kebijakan keamanan Lelana.id.

        Password harus memenuhi empat kriteria berikut:
        - Minimal satu huruf kecil (a–z),
        - Minimal satu huruf besar (A–Z),
        - Minimal satu angka (0–9),
        - Minimal satu karakter spesial dari himpunan @$!%*?&#.

        Validasi ini dipanggil otomatis oleh WTForms selama proses registrasi.
        Jika salah satu kriteria tidak terpenuhi, ValidationError akan dilemparkan
        dengan pesan spesifik untuk membantu pengguna memperbaiki input.

        Args:
            password (wtforms.Field): Field password dari formulir registrasi.
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
        """
        Memastikan username yang diinput belum digunakan oleh pengguna lain.

        Dipanggil otomatis oleh WTForms saat validasi formulir. Jika username
        sudah ada di database, akan memicu ValidationError.

        Args:
            username (wtforms.Field): Field username dari formulir.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username tersebut sudah digunakan. Silakan pilih yang lain.')
    
    def validate_email(self, email):
        """
        Memastikan email yang diinput belum terdaftar di sistem.

        Dipanggil otomatis selama validasi formulir pendaftaran. Mencegah duplikasi
        akun berdasarkan alamat email.

        Args:
            email (wtforms.Field): Field email dari formulir.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email tersebut sudah terdaftar. Silakan gunakan email lain.')

class LoginForm(FlaskForm):
    """
    Formulir login pengguna yang telah terdaftar.

    Mengizinkan pengguna masuk dengan email dan password, serta opsi "Ingat Saya"
    untuk sesi berkepanjangan. Digunakan di rute /auth/login.

    Field:
        email (StringField): Email terdaftar.
        password (PasswordField): Kata sandi akun.
        remember (BooleanField): Opsi untuk mempertahankan sesi.
        submit (SubmitField): Tombol login.
    """
    email = StringField('Email', 
                        validators=[DataRequired(message='Email wajib diisi.'), 
                                    Email(message='Format email tidak valid.')])
    password = PasswordField('Password', 
                             validators=[DataRequired(message='Password wajib diisi.')])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Login')

class WisataForm(FlaskForm):
    """
    Formulir untuk menambahkan atau memperbarui data destinasi wisata.

    Digunakan oleh admin untuk mengelola konten wisata. Mendukung input opsional
    koordinat GPS (latitude/longitude) untuk integrasi peta di frontend.

    Field:
        nama (StringField): Nama destinasi wisata.
        kategori (StringField): Jenis wisata (alam, budaya, kuliner, dll).
        lokasi (StringField): Alamat atau deskripsi lokasi.
        deskripsi (TextAreaField): Informasi lengkap tentang wisata.
        gambar_url (StringField): URL gambar utama (opsional).
        latitude (FloatField): Koordinat lintang (opsional).
        longitude (FloatField): Koordinat bujur (opsional).
        submit (SubmitField): Simpan perubahan.
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
    """
    Formulir untuk mengelola event budaya di wilayah Jawa Tengah.

    Digunakan oleh admin untuk memasukkan event dengan tanggal pasti dan lokasi.
    Penyelenggara bersifat opsional untuk fleksibilitas data.

    Field:
        nama (StringField): Nama event.
        tanggal (DateField): Tanggal pelaksanaan (format YYYY-MM-DD).
        lokasi (StringField): Tempat penyelenggaraan.
        deskripsi (TextAreaField): Detail acara.
        penyelenggara (StringField): Nama komunitas/lembaga (opsional).
        submit (SubmitField): Simpan event.
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
    """
    Formulir pengiriman ulasan pengalaman wisata oleh pengguna terautentikasi.

    Memungkinkan pengguna memberikan rating (1–5), komentar wajib, dan unggah
    hingga beberapa foto pendukung. Validasi file hanya menerima format gambar.

    Field:
        rating (IntegerField): Nilai ulasan antara 1 hingga 5.
        komentar (TextAreaField): Ulasan teks wajib.
        foto (MultipleFileField): Unggahan foto opsional (jpg/png/jpeg).
        submit (SubmitField): Kirim ulasan.
    """
    rating = IntegerField('Rating (1-5)', 
                          validators=[DataRequired(), NumberRange(min=1, max=5, message='Rating harus antara 1 dan 5.')])
    komentar = TextAreaField('Komentar Anda', 
                             validators=[DataRequired(message='Komentar tidak boleh kosong.')])
    foto = MultipleFileField('Unggah Foto (Opsional)', 
                             validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Hanya gambar (jpg, png, jpeg) yang diizinkan!')])
    submit = SubmitField('Kirim Review')

def get_all_wisata():
    """
    Mengambil semua entitas wisata dari database, diurutkan berdasarkan nama.

    Digunakan sebagai query factory untuk field seleksi ganda (misalnya pada
    PaketWisataForm dan ItinerariForm) agar daftar destinasi selalu terurut
    dan konsisten di antarmuka pengguna.

    Returns:
        list[Wisata]: Daftar objek Wisata yang telah diurutkan secara alfabetis.
    """
    return Wisata.query.order_by(Wisata.nama).all()

class PaketWisataForm(FlaskForm):
    """
    Formulir untuk membuat paket wisata gabungan dari beberapa destinasi.

    Admin dapat memilih beberapa wisata dari daftar yang tersedia dan menetapkan
    harga paket. Menggunakan QuerySelectMultipleField untuk integrasi dinamis
    dengan data Wisata yang ada di database.

    Field:
        nama (StringField): Nama paket wisata.
        deskripsi (TextAreaField): Penjelasan isi paket.
        harga (IntegerField): Harga dalam Rupiah.
        destinasi (QuerySelectMultipleField): Daftar wisata yang dipilih.
        submit (SubmitField): Simpan paket.
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
    """
    Formulir untuk menyusun itinerari perjalanan berbasis destinasi yang ada.

    Memungkinkan pengguna (atau admin) membuat rencana perjalanan dengan memilih
    beberapa tempat wisata dari database. Judul wajib, deskripsi opsional.

    Field:
        judul (StringField): Nama itinerari.
        deskripsi (TextAreaField): Cerita atau catatan perjalanan (opsional).
        wisata_termasuk (QuerySelectMultipleField): Pilihan destinasi wisata.
        submit (SubmitField): Simpan itinerari.
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
    """
    Formulir khusus admin untuk mengelola data pengguna (termasuk peran).

    Memvalidasi keunikan username dan email hanya jika nilai tersebut diubah,
    sehingga admin dapat menyimpan tanpa mengganti data yang sama. Mendukung
    perubahan role antara 'user' dan 'admin'.

    Field:
        username (StringField): Nama pengguna (4–25 karakter).
        email (StringField): Email valid.
        role (SelectField): Peran pengguna ('user' atau 'admin').
        submit (SubmitField): Simpan perubahan.

    Catatan:
        Validasi custom pada username dan email hanya dijalankan jika nilai
        baru berbeda dari data asli, untuk menghindari false positive saat edit.
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
        """
        Memvalidasi keunikan username hanya jika nilainya diubah dari data asli.

        Menghindari kesalahan validasi saat admin menyimpan formulir tanpa
        mengganti username. Jika username baru sudah dipakai pengguna lain,
        lemparkan ValidationError.

        Args:
            username (wtforms.Field): Field username dari formulir edit.
        """
        if username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username tersebut sudah digunakan.')

    def validate_email(self, email):
        """
        Memvalidasi keunikan email hanya jika nilainya diubah.

        Sama seperti validasi username, ini mencegah false positive saat admin
        hanya mengubah role tanpa menyentuh email.

        Args:
            email (wtforms.Field): Field email dari formulir edit.
        """
        if email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email tersebut sudah terdaftar.')