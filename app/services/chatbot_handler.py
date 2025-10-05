import requests
from flask import current_app

def search_web(query: str):
    """Melakukan pencarian web menggunakan Serper API berdasarkan kueri pengguna.

    Mengambil hasil organik dari Google Search melalui layanan Serper.dev.
    Memerlukan kunci API yang dikonfigurasi di `SERPER_API_KEY`.

    Args:
        query (str): Kueri pencarian dari pengguna.

    Returns:
        list: Daftar hasil pencarian organik (masing-masing berupa dict), 
              atau daftar kosong jika gagal atau tidak ada hasil.
    """
    serper_api_key = current_app.config.get('SERPER_API_KEY')
    if not serper_api_key:
        current_app.logger.error("Kunci API Serper belum dikonfigurasi.")
        return []
    
    headers = {
        "X-API-KEY": serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}

    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        return data.get("organic", [])
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error saat mencari di Serper: {e}")
        return []
    
def call_gemini(prompt: str):
    """Mengirim prompt ke Google Gemini API dan mengambil respons teks.

    Menggunakan model `gemini-2.0-flash` untuk menghasilkan jawaban berdasarkan
    konteks yang diberikan. Memerlukan kunci API yang dikonfigurasi di `GEMINI_API_KEY`.

    Args:
        prompt (str): Teks prompt yang akan dikirim ke model Gemini.

    Returns:
        str or None: Respons teks dari model jika sukses; None jika terjadi error.
    """
    gemini_api_key = current_app.config.get('GEMINI_API_KEY')
    if not gemini_api_key:
        return "Error: Kunci API Gemini belum dikonfigurasi."

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(gemini_url, headers=headers, json=body)
        resp.raise_for_status()
        j = resp.json()

        return j["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        current_app.logger.error(f'Error saat memanggil Gemini: {e}')
        return None
    
def get_bot_response(user_query: str):
    """Menghasilkan respons chatbot berdasarkan pertanyaan pengguna.

    Fungsi ini:
    1. Melakukan pencarian web untuk mengumpulkan informasi kontekstual.
    2. Jika ada hasil, menyusun ringkasan dan mengirimkannya ke Gemini sebagai konteks.
    3. Jika tidak ada hasil, langsung meminta Gemini menjawab berdasarkan pengetahuannya.
    4. Mengembalikan jawaban yang ramah dan sesuai dengan persona "Putri", asisten Lelana.id.

    Args:
        user_query (str): Pertanyaan atau pernyataan dari pengguna.

    Returns:
        str: Jawaban dari chatbot dalam bentuk teks yang telah diformat.
    """
    search_results = search_web(user_query)

    if not search_results:
        current_app.logger.warning("Pencarian web tidak memberikan hasil. Menggunakan fallback ke Gemini langsung.")
        prompt = (
            f"Kamu adalah Putri, asisten virtual yang ramah dan membantu untuk platform wisata Lelana.id. "
            f"Jawab pertanyaan berikut se-informatif mungkin: \"{user_query}\""
        )
    else:
        summary = ""
        for item in search_results[:3]: # Mengambil 3 hasil teratas
            t = item.get("title", "")
            s = item.get("snippet", "")
            summary += f"- {t}: {s}\n"

        prompt = (
            f"Kamu adalah Putri, asisten virtual yang ramah, ceria, dan sangat membantu untuk platform wisata Lelana.id.\n"
            f"Berikut adalah beberapa informasi relevan dari web terkait pertanyaan pengguna:\n\n"
            f"{summary}\n\n"
            f"Berdasarkan informasi tersebut, berikan jawaban yang hangat, informatif, dan mudah dibaca untuk pertanyaan berikut: \"{user_query}\""
        )

    answer = call_gemini(prompt)

    if answer is None:
        "Maaf, sepertinya Putri sedang mengalami sedikit kendala teknis. Coba lagi beberapa saat lagi ya! 😢"
    
    return answer.strip()