from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Mengirim email secara asinkron dalam konteks aplikasi terpisah.

    Digunakan untuk menghindari pemblokiran permintaan HTTP utama saat mengirim email.

    Args:
        app (Flask): Instance aplikasi Flask untuk memulihkan konteks.
        msg (Message): Objek pesan email yang akan dikirim.
    """
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """Mengirim email HTML menggunakan template Jinja2 secara asinkron.

    Fungsi ini merender template email berdasarkan nama file template,
    lalu mengirimkannya ke penerima yang ditentukan dalam thread terpisah.

    Args:
        to (str): Alamat email penerima.
        subject (str): Subjek email.
        template (str): Nama file template (tanpa ekstensi .html) di direktori templates.
        **kwargs: Variabel konteks untuk dilewatkan ke template Jinja2.

    Returns:
        Thread: Objek thread yang menjalankan pengiriman email.
    """
    app = current_app._get_current_object()
    msg = Message(
        subject,
        sender=app.config['MAIL_SENDER'],
        recipients=[to]
    )
    
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

    return thr