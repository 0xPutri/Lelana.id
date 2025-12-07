from unittest.mock import patch
from app.services.email_handler import send_email
from app import mail
from threading import Thread


class SyncThread(Thread):
    """Kelas Thread kustom yang dirancang untuk menjalankan target dalam mode sinkron selama pengujian.

    Kelas ini secara spesifik menimpa perilaku default `threading.Thread` Python
    untuk tujuan pengujian. Dengan menimpa metode `start()`, eksekusi fungsi
    pengiriman email dipaksa berjalan secara in-line (sinkron),
    memastikan proses selesai sebelum validasi hasil.
    """

    def __init__(self, target, args, **kwargs):
        """Menginisialisasi instance SyncThread dengan argumen Thread standar.

        Args:
            target: Fungsi yang akan dijalankan oleh thread secara sinkron.
            args: Argumen posisi yang diteruskan ke fungsi target.
            kwargs: Argumen kata kunci yang diteruskan ke fungsi target.
        """
        super().__init__(target=target, args=args, **kwargs)

    def start(self):
        """Menimpa metode standar `start()` untuk memaksa eksekusi fungsi secara sinkron.

        Alih-alih membuat thread baru yang berjalan secara asinkron, metode ini
        langsung memanggil `self.run()`, memastikan pengujian email selesai
        secara deterministik dan andal dalam urutan eksekusi utama.
        """
        self.run()


@patch('app.services.email_handler.Thread', new=SyncThread)
def test_send_email(app):
    """Menguji fungsionalitas pengiriman email untuk skenario pengiriman konfirmasi akun.

    Memastikan bahwa fungsi `send_email` berhasil membuat dan mengirimkan
    tepat satu pesan email. Pengujian memverifikasi subjek, penerima,
    dan konten HTML template (termasuk variabel dinamis seperti username dan token)
    sudah sesuai dengan yang diharapkan.

    Args:
        app: Objek aplikasi Flask, digunakan untuk konteks permintaan dan konfigurasi.
    """
    mock_user = type('User', (object,), {'username': 'testuser'})()
    token = 'dummy-token'

    with app.test_request_context():
        app.config['MAIL_SENDER'] = 'noreply@lelana.id'
        app.config['SERVER_NAME'] = 'localhost'

        with mail.record_messages() as outbox:
            send_email(
                to='penerima@example.com',
                subject='Konfirmasi Akun',
                template='auth/email/confirm',
                user=mock_user,
                token=token
            )

            assert len(outbox) == 1
            msg = outbox[0]

            assert msg.subject == 'Konfirmasi Akun'
            assert msg.recipients == ['penerima@example.com']
            assert 'Yth. <strong>testuser</strong>,' in msg.html
            assert 'Untuk menyelesaikan proses pendaftaran' in msg.html
            assert 'dummy-token' in msg.html