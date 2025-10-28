# 🌿 Lelana.id

> Platform digital berbasis komunitas untuk mengeksplor dan mempromosikan destinasi wisata Jawa Tengah — mulai dari Banyumas dan sekitarnya. ✨

## Tentang Proyek

**Lelana.id** adalah aplikasi web berbasis **Flask (Python)** yang berfungsi sebagai direktori wisata interaktif. Tidak hanya menampilkan informasi destinasi dan event budaya, tetapi juga membuka ruang bagi pengguna untuk berbagi cerita perjalanan dan ulasan pengalaman mereka.

## Tujuan Utama

* **Menginformasikan:** Menyediakan data wisata yang akurat dan terkurasi.
* **Menginspirasi:** Memberi ruang bagi pengguna untuk berbagi cerita dan ulasan.
* **Mempromosikan:** Menjadi media promosi bagi destinasi lokal dan event budaya.
* **Menghubungkan:** Membangun komunitas digital pecinta wisata.

## Fitur Utama

| Modul            | Fitur                                                      | Akses           |
| ---------------- | ---------------------------------------------------------- | --------------- |
| **Autentikasi**  | Registrasi, Login, Logout dengan validasi keamanan         | Tamu & Pengguna |
| **Wisata**       | Daftar & detail destinasi, ulasan (rating, komentar, foto) | Semua           |
| **Event Budaya** | Daftar & detail event budaya                               | Semua           |
| **Paket Wisata** | Manajemen paket dan promosi wisata                         | Admin           |
| **Itinerari**    | Pengguna dapat membuat dan berbagi cerita perjalanan       | User & Admin    |
| **Admin Panel**  | CRUD data wisata, event, paket, dan pengguna               | Admin           |

## Arsitektur Sistem

**Backend:** Python Flask
**Database:** SQLite
**Frontend:** HTML5, CSS3, JavaScript (ES6)
**Peta:** Leaflet.js + OpenStreetMap

Arsitektur modular menggunakan *Blueprints* untuk menjaga skalabilitas dan kemudahan pemeliharaan.

## Teknologi Utama

| Kategori        | Teknologi                                                            |
| --------------- | -------------------------------------------------------------------- |
| Framework       | Flask (Python)                                                       |
| Database        | SQLite 3                                                             |
| Library         | Flask-SQLAlchemy, Flask-Login, Flask-Limiter, Werkzeug, python-magic |
| Testing         | Pytest                                                               |
| Version Control | Git                                                                  |

## Kebutuhan Non-Fungsional

* Password disimpan dalam bentuk hash (Werkzeug Security)
* Validasi file berdasarkan MIME type (bukan ekstensi)
* Antarmuka responsif untuk desktop & mobile
* Struktur modular untuk maintainability tinggi

## Pengujian

Dilakukan dalam tiga tahap utama:

1. **Unit Test:** Model, form, dan service logic.
2. **Integration Test:** Rute autentikasi, publik, dan proteksi akses.
3. **Admin Test:** Pengujian CRUD & otorisasi peran admin.

## Tim Pengembang 💞

| Nama                          | Peran                 |
| ----------------------------- | --------------------- |
| Willyan Hyuga Pratama         | UI/UX Designer & (PM) |
| Buswiryawan Raditya Boenyamin | QA Tester             |
| Rozhak                        | Backend Developer     |
| Arjun Ahmad Santoso           | Frontend Developer    |

## Catatan

README ini bersifat ringkas dan digunakan untuk laporan progres proyek. Versi dokumentasi lengkap dapat ditemukan di dokumen **SKPL (Spesifikasi Kebutuhan Perangkat Lunak)**.

> *"Menjelajah bumi, menyatukan cerita — bersama **Lelana.id**."* 💚