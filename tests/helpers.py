class AuthActions:
    """Kumpulan aksi pembantu (helper actions) yang terstruktur untuk simulasi
    interaksi pengguna dengan seluruh endpoint autentikasi (Auth) selama pengujian.

    Kelas ini digunakan di seluruh rangkaian pengujian untuk menyederhanakan
    proses penyiapan prasyarat pengujian seperti pendaftaran pengguna baru atau login,
    tanpa perlu menulis ulang logika permintaan POST/GET berulang kali.
    """

    def __init__(self, client):
        """Menginisialisasi instance dari AuthActions dengan objek klien pengujian HTTP yang spesifik.

        Args:
            client: Objek klien pengujian (misalnya: Flask Test Client) yang
                    digunakan untuk membuat dan mengirimkan permintaan HTTP simulasi.
        """
        self._client = client

    def login(self, email, password):
        """Mensimulasikan upaya autentikasi pengguna ke dalam aplikasi Lelana.id secara terperinci.

        Mengirimkan permintaan POST ke '/auth/login' dengan kredensial
        yang diberikan, dan mengikuti pengalihan (redirect) jika berhasil atau gagal.

        Args:
            email: Email pengguna untuk login.
            password: Kata sandi pengguna untuk login.

        Returns:
            Response: Objek respons dari klien pengujian setelah permintaan selesai.
        """
        return self._client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)

    def logout(self):
        """Mensimulasikan proses pengakhiran sesi pengguna dari aplikasi Lelana.id secara resmi.

        Mengirimkan permintaan GET ke '/auth/logout' dan mengikuti pengalihan
        (redirect), yang diharapkan akan mengakhiri sesi pengguna.

        Returns:
            Response: Objek respons dari klien pengujian setelah permintaan selesai.
        """
        return self._client.get('/auth/logout', follow_redirects=True)

    def register(self, username, email, password, confirm_password):
        """Mensimulasikan proses inisiasi pendaftaran akun pengguna baru ke dalam sistem Lelana.id.

        Mengirimkan permintaan POST ke '/auth/register' dengan data pengguna
        baru dan mengikuti pengalihan setelahnya.

        Args:
            username: Nama pengguna yang akan didaftarkan.
            email: Alamat email pengguna yang akan didaftarkan.
            password: Kata sandi baru.
            confirm_password: Konfirmasi kata sandi, harus sesuai dengan 'password'.

        Returns:
            Response: Objek respons dari klien pengujian setelah permintaan selesai.
        """
        return self._client.post('/auth/register', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        }, follow_redirects=True)