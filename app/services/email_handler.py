from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Mengirim email secara asinkron dalam konteks aplikasi terpisah.

    Fungsi ini dieksekusi di dalam sebuah thread untuk menghindari pemblokiran
    permintaan HTTP utama saat proses pengiriman email berjalan.

    Args:
        app (Flask): Instance aplikasi Flask untuk memulihkan konteks.
        msg (Message): Objek pesan email Flask-Mail yang akan dikirim.
    """
    # Memastikan operasi email dijalankan dalam konteks aplikasi yang benar
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """Merender dan mengirim email HTML secara asinkron.

    Fungsi ini membuat pesan, merender template email dari Jinja2, lalu
    memulai thread baru untuk mengirimkannya agar tidak memblokir proses utama.

    Args:
        to (str): Alamat email penerima.
        subject (str): Subjek email.
        template (str): Path ke file template (tanpa ekstensi .html).
        **kwargs: Variabel konteks untuk dilewatkan ke template Jinja2.

    Returns:
        Thread: Objek thread yang menjalankan proses pengiriman email.
    """
    # Mendapatkan instance aplikasi saat ini untuk dilewatkan ke thread
    app = current_app._get_current_object()
    # Membuat objek pesan email dengan subjek, pengirim, dan penerima
    msg = Message(
        subject,
        sender=app.config['MAIL_SENDER'],
        recipients=[to]
    )
    
    # Merender template HTML dan menyetelnya sebagai isi email
    msg.html = render_template(template + '.html', **kwargs)
    # Membuat thread baru untuk menjalankan fungsi send_async_email
    thr = Thread(target=send_async_email, args=[app, msg])
    # Memulai eksekusi thread
    thr.start()

    return thr
