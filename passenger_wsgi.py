import os
import sys
from dotenv import load_dotenv

# Tambahkan path direktori proyek Anda ke sys.path.
# Ganti '/path/to/your/project' dengan path absolut ke direktori Lelana.id Anda
# jika file ini akan dipindahkan atau dijalankan dari lokasi yang berbeda.
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Memuat variabel lingkungan dari file .env
dotenv_path = os.path.join(project_home, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Impor application factory dari modul app
from app import create_app

# Buat instance aplikasi untuk server WSGI.
# Pastikan variabel lingkungan FLASK_CONFIG diatur ke 'production' di lingkungan server Anda.
# Jika tidak diatur, file ini akan menggunakan 'production' sebagai default.
application = create_app(os.getenv('FLASK_CONFIG') or 'production')
