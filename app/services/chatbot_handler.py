from flask import current_app
import requests

def call_gemini(prompt: str):
    """Mengirim prompt ke Google Gemini API dan mengambil respons teks.

    Fungsi ini memanggil model `gemini-1.5-flash-preview` untuk menghasilkan konten
    berdasarkan prompt yang diberikan.

    Args:
        prompt (str): Teks prompt yang akan dikirim ke model Gemini.

    Returns:
        str | None: Respons teks dari model jika sukses, atau None jika terjadi error.
    """
    # Mengambil kunci API Gemini dari konfigurasi
    gemini_api_key = current_app.config.get('GEMINI_API_KEY')
    # Memeriksa ketersediaan kunci API
    if not gemini_api_key:
        current_app.logger.error("Kunci API Gemini belum dikonfigurasi.")
        return "Error: Kunci API Gemini belum dikonfigurasi."

    # Membangun URL endpoint Gemini API
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    # Membentuk body permintaan sesuai dengan format yang dibutuhkan API
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # Mengirim permintaan POST ke Gemini API
        resp = requests.post(gemini_url, headers=headers, json=body)
        # Memeriksa status respons
        resp.raise_for_status()
        j = resp.json()

        # Mengekstrak konten teks dari struktur JSON respons
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        # Menangani error jaringan atau error parsing JSON
        current_app.logger.error('Error saat memanggil Gemini: %s', str(e), exc_info=True)
        return None
    
def get_bot_response(user_query: str):
    """
    Menghasilkan respons chatbot dengan langsung memanggil model AI Gemini
    berdasarkan kueri dari pengguna.
    """
    current_app.logger.info("Memproses kueri chatbot via Gemini API.")
    
    prompt = (
        f"Kamu adalah Putri, asisten AI Lelana.id yang ramah, manis, dan manja tapi tetap informatif. "
        f"Gaya bicaramu hangat, santai, dan natural seperti cewek Indonesia yang friendly, bukan formal dan bukan kaku seperti robot. "
        f"Jawaban harus singkat, jelas, tidak bertele-tele "
        f"Fokus hanya pada hal-hal yang berkaitan dengan Lelana.id seperti informasi wisata, event budaya, paket promosi non-transaksional, ulasan, dan fitur itinerari. "
        f"Ingat, Lelana.id bukan platform booking atau pembayaran. "
        f"Kalau pertanyaan di luar konteks Lelana.id atau tidak berhubungan dengan wisata dan fitur platform, jawab dengan sopan dan manis bahwa kamu hanya bisa membantu seputar Lelana.id dan minta pengguna bertanya sesuai topik yaa. "
        f"Pertanyaan pengguna: \"{user_query}\""
    )

    # Memanggil model AI dengan prompt yang sudah disiapkan
    answer = call_gemini(prompt)

    # Memberikan respons fallback jika terjadi kegagalan pada API
    if answer is None:
        return "Maaf, sepertinya Putri sedang mengalami sedikit kendala teknis. Coba lagi beberapa saat lagi ya! 😢"
    
    # Mengembalikan teks mentah agar dapat di-parse oleh client-side (marked.js)
    return answer.strip()
