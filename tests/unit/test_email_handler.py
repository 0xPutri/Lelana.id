from app.services.email_handler import send_email
from app import mail

def test_send_email(app):
    """Menguji fungsionalitas pengiriman email secara sinkron.

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