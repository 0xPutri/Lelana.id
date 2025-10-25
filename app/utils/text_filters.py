import re
from markdown_it import MarkdownIt
from better_profanity import profanity

def init_profanity_filter(app):
    """Menginisialisasi penyaring kata kasar dengan daftar bawaan dan tambahan.

    Memuat daftar kata kasar default dari library, lalu menambahkan kata-kata
    kustom dari konfigurasi aplikasi (jika tersedia) melalui kunci 'BAD_WORDS_ID'.

    Args:
        app (Flask): Instance aplikasi Flask untuk mengakses konfigurasi.
    """
    profanity.load_censor_words()
    bad_words = app.config.get('BAD_WORDS_ID', [])
    if bad_words:
        profanity.add_censor_words(bad_words)

def _normalize_text(text: str) -> str:
    """Menormalisasi teks untuk meningkatkan deteksi kata kasar.

    Mengubah teks menjadi huruf kecil dan mengganti pengulangan dua karakter
    atau lebih berturut-turut menjadi satu karakter (misal: 'annjjinnng' → 'anjing').

    Args:
        text (str): Teks input yang akan dinormalisasi.

    Returns:
        str: Teks yang telah dinormalisasi.
    """
    text = text.lower()
    text = re.sub(r'(.)\1+', r'\1', text)
    
    return text

def censor_text(text: str) -> str:
    """Menyensor teks dari kata kasar dengan mempertahankan format asli sebisa mungkin.

    Fungsi ini:
    1. Memvalidasi input (mengembalikan aslinya jika bukan string atau kosong).
    2. Menormalisasi teks untuk mendeteksi variasi kata kasar.
    3. Jika ditemukan kata kasar, menyensor hanya bagian sensitif dan mempertahankan
       kapitalisasi serta tanda baca asli dari teks input.

    Args:
        text (str): Teks yang akan diperiksa dan disensor.

    Returns:
        str: Teks asli jika tidak mengandung kata kasar, atau versi tersensor jika ada.
    """
    if not isinstance(text, str) or not text.strip():
        return text
    
    normalized_text = _normalize_text(text)

    if not profanity.contains_profanity(normalized_text):
        return text
    
    censored_normalized_text = profanity.censor(normalized_text)

    original_parts = re.split(r'([\s.,!?-]+)', text)
    censored_normalized_parts = re.split(r'([\s.,!?-]+)', censored_normalized_text)

    if len(original_parts) != len(censored_normalized_parts):
        return censored_normalized_text
    
    result_parts = []
    for i, part in enumerate(censored_normalized_parts):
        if '****' in part:
            result_parts.append(part)
        else:
            result_parts.append(original_parts[i])

    return "".join(result_parts)

def markdown_to_html(text):
    """Mengonversi teks Markdown sederhana menjadi HTML dengan aman.

    Fungsi ini:
    - Menggantikan escape sequence '\\n' menjadi newline asli,
    - Memproses setiap baris secara terpisah menggunakan MarkdownIt dalam mode CommonMark,
    - Menonaktifkan rendering HTML mentah untuk keamanan (XSS prevention),
    - Mengaktifkan linkify untuk mengubah URL otomatis menjadi tautan,
    - Menggabungkan hasil dengan tag <br> untuk mempertahankan jeda baris.

    Args:
        text (str): Teks input yang mungkin mengandung sintaks Markdown dasar.

    Returns:
        str: Teks yang telah dikonversi ke HTML aman, atau nilai asli jika input tidak valid.
    """
    if not isinstance(text, str) or not text.strip():
        return text
    
    standardized_text = text.replace('\\n', '\n')
    
    lines = standardized_text.split('\n')
    
    md = MarkdownIt('commonmark', {'html': False, 'linkify': True})
    md.enable('linkify')

    rendered_lines = [md.renderInline(line) for line in lines]
    
    return '<br>'.join(rendered_lines)