from flask import render_template, current_app
from flask_mail import Message
from app import mail

def send_email(to, subject, template, **kwargs):
    """Merender dan mengirim email HTML secara langsung (synchronous).

    Fungsi ini membuat pesan, merender template dari Jinja2, dan langsung
    mengirimkannya. Proses ini akan memblokir request utama hingga email
    selesai terkirim.

    Args:
        to (str): Alamat email penerima.
        subject (str): Subjek email.
        template (str): Path ke file template (tanpa ekstensi .html).
        **kwargs: Variabel konteks untuk dilewatkan ke template Jinja2.
    """
    # Mendapatkan instance aplikasi saat ini untuk mengakses konfigurasi
    app = current_app._get_current_object()
    
    # Membuat objek pesan email dengan subjek, pengirim, dan penerima
    msg = Message(
        subject,
        sender=app.config['MAIL_SENDER'],
        recipients=[to]
    )
    
    # Merender template HTML dan menyetelnya sebagai isi email
    msg.html = render_template(template + '.html', **kwargs)
    
    # Mengirim email secara langsung dan mencatat hasilnya
    try:
        mail.send(msg)
        app.logger.info(f"Email untuk '{subject}' berhasil dikirim ke {to}")
    except Exception as e:
        app.logger.error(f"Gagal mengirim email ke {to}. Subjek: '{subject}'. Error: {e}")
        # raise e