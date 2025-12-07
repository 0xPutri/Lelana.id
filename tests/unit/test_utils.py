import pytest
from app.utils.text_filters import censor_text, _normalize_text
from better_profanity import profanity


@pytest.fixture(autouse=True)
def setup_profanity_filter():
    """Fixture Pytest untuk menginisialisasi dan menyiapkan kamus kata-kata kotor.

    Fungsi ini dijalankan secara otomatis (autouse=True) sebelum setiap
    pengujian di modul ini. Bertanggung jawab untuk memuat daftar kata-kata
    kotor bawaan dan menambahkan kata kotor spesifik Bahasa Indonesia
    ('anjing', 'babi') ke dalam filter.
    """
    profanity.load_censor_words()
    profanity.add_censor_words(["anjing", "babi"])


def test_censor_text_with_profanity():
    """Menguji skenario sensor teks dasar yang mengandung kata-kata kotor terdaftar."""
    assert censor_text("Dasar kau anjing") == "Dasar kau ****"


def test_censor_text_without_profanity():
    """Menguji skenario teks yang bersih dan tidak mengandung kata-kata yang harus disensor."""
    assert censor_text("Ini adalah kalimat yang bersih.") == "Ini adalah kalimat yang bersih."


def test_censor_text_with_repeated_letters_profanity():
    """Menguji kemampuan sensor untuk mengenali kata kotor meskipun terdapat pengulangan karakter."""
    assert censor_text("Dasar anjiiing tidak berguna") == "Dasar **** tidak berguna"


def test_censor_text_with_mixed_case_profanity():
    """Menguji sensitivitas filter terhadap penggunaan huruf besar dan huruf kecil (mixed case)."""
    assert censor_text("Kamu seperti BaBi!") == "Kamu seperti ****!"


def test_censor_text_with_empty_string():
    """Menguji perilaku fungsionalitas sensor ketika menerima input berupa string kosong."""
    assert censor_text("") == ""


def test_censor_text_with_whitespace_string():
    """Menguji perilaku fungsionalitas sensor ketika menerima input hanya berisi spasi."""
    assert censor_text("   ") == "   "


def test_censor_text_with_non_string_input():
    """Menguji stabilitas dan perilaku fungsi sensor saat menerima input non-string (misalnya integer)."""
    assert censor_text(123) == 123


def test_normalize_text_with_repeated_chars():
    """Menguji fungsi utilitas internal `_normalize_text` untuk membersihkan pengulangan karakter."""
    assert _normalize_text("annjjinnnggg") == "anjing"
    assert _normalize_text("bbaaabbbiii") == "babi"


def test_normalize_text_lowercase():
    """Menguji fungsi utilitas internal `_normalize_text` untuk konversi teks ke huruf kecil."""
    assert _normalize_text("Anjing") == "anjing"


def test_censor_text_preserves_punctuation():
    """Menguji apakah proses sensor tetap mempertahankan tanda baca di sekitar kata kotor."""
    assert censor_text("Hey, anjing!") == "Hey, ****!"