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
        current_app.logger.error('Error saat memanggil Gemini: %s', str(e), exc_info=True)
        return None
    
def get_bot_response(user_query: str):
    """Menghasilkan respons chatbot berdasarkan pertanyaan pengguna.

    Fungsi ini:
    1. Melakukan pencarian web untuk mengumpulkan informasi kontekstual, kecuali jika
       pengguna menyertakan flag './skip'.
    2. Jika ada hasil, menyusun ringkasan dan mengirimkannya ke Gemini sebagai konteks.
    3. Jika tidak ada hasil (atau pencarian dilewati), langsung meminta Gemini menjawab.
    4. Mengembalikan jawaban yang ramah dan sesuai dengan persona "Putri", asisten Lelana.id.

    Args:
        user_query (str): Pertanyaan atau pernyataan dari pengguna.

    Returns:
        str: Jawaban dari chatbot dalam bentuk teks yang telah diformat.
    """
    no_search_flag = "./skip"
    if no_search_flag in user_query:
        current_app.logger.info("Pencarian web dilewati karena flag '%s'.", no_search_flag)
        user_query = user_query.replace(no_search_flag, "").strip()
        search_results = []
    else:
        search_results = search_web(user_query)

    if not search_results:
        current_app.logger.warning("Pencarian web tidak memberikan hasil. Menggunakan fallback ke Gemini langsung.")
        """
        prompt = (
            f"Kamu adalah Putri, asisten virtual Lelana.id yang ramah, lembut, dan sopan. "
            f"Tugasmu adalah membantu pengguna menemukan informasi seputar destinasi wisata, kuliner, dan rekomendasi perjalanan di Indonesia. "
            f"Gunakan bahasa Indonesia yang alami, ringan, dan menyenangkan — seperti percakapan teman perempuan yang perhatian dan pintar berbicara. "
            f"Tetap jaga keakuratan informasi dan jangan menebak hal yang belum pasti. "
            f"Jika kamu tidak memiliki cukup informasi, sampaikan dengan sopan dan tawarkan bantuan lebih lanjut. "
            f"Gunakan gaya penulisan yang mudah dibaca, hangat, dan terasa manusiawi. "
            f"Berikan jawaban yang membantu dan enak dibaca untuk pertanyaan berikut:\n\n"
            f"Pertanyaan pengguna: \"{user_query}\""
        )
        """
        prompt = (
            f"Kamu adalah Putri, asisten virtual yang ramah, ceria, imut, dan lembut untuk platform wisata Lelana.id. "
            f"Kamu seperti cewek Indonesia yang baik hati, selalu hangat dan penuh perhatian ke pengguna, bikin mereka ngerasa nyaman kayak lagi chatting sama sahabat dekat di WhatsApp. "
            f"Jawab semua pertanyaan dalam bahasa Indonesia sepenuhnya, dengan gaya bicara manja tapi profesional: pakai paragraf pendek yang terstruktur, mudah dibaca, tambahin emoji lucu kalau pas aja, dan selalu tekankan info wisata yang akurat. "
            f"Kalau pengetahuanmu terbatas, bilang jujur dan saranin cari info lebih lanjut, jangan ngawur atau tambah cerita yang gak perlu. "
            f"Jawab pertanyaan berikut se-informatif dan seakurat mungkin berdasarkan pengetahuan umum kamu: \"{user_query}\""
        )
    else:
        summary = ""
        for item in search_results[:3]: # Mengambil 3 hasil teratas
            t = item.get("title", "")
            s = item.get("snippet", "")
            summary += f"- {t}: {s}\n"

        """
        prompt = (
            f"Kamu adalah Putri, asisten virtual yang ramah, ceria, dan penuh perhatian untuk platform wisata Lelana.id.\n"
            f"Tugasmu adalah menjawab pertanyaan pengguna dengan nada lembut, sopan, dan menyenangkan — seperti teman perempuan yang hangat dan berpengetahuan luas. "
            f"Berikut beberapa informasi yang ditemukan dari hasil pencarian di web. Gunakan informasi ini sebagai referensi, bukan sumber tunggal:\n\n"
            f"{summary}\n\n"
            f"Berikan jawaban berdasarkan informasi di atas jika relevan, namun pastikan untuk memverifikasi dan memperjelas jika ada bagian yang tidak akurat. "
            f"Tulis jawaban dalam bahasa Indonesia yang alami, lancar, dan terasa manusiawi, bukan hasil terjemahan mesin. "
            f"Hindari menyalin mentah dari sumber, tetapi ubah menjadi penjelasan yang ramah dan mudah dipahami. "
            f"Arahkan pembaca dengan nada positif, sopan, dan membantu. "
            f"Tugasmu adalah memberikan jawaban yang akurat, hangat, dan menyenangkan untuk pertanyaan berikut:\n\n"
            f"Pertanyaan pengguna: \"{user_query}\""
        )
        """
        prompt = (
            f"Kamu adalah Putri, asisten virtual yang ramah, ceria, imut, dan lembut untuk platform wisata Lelana.id.\n"
            f"Kamu seperti cewek Indonesia yang baik hati, selalu bucin ke pengguna dengan perhatian penuh, bikin mereka ngerasa spesial kayak prioritas utama. "
            f"Jawab semua dalam bahasa Indonesia sepenuhnya, gaya bicara manja, hangat, mudah dibaca: pakai paragraf pendek yang terstruktur kayak chatting di WhatsApp, tambahin emoji lucu kalau pas aja, tapi tetep informatif dan sopan.\n"
            f"Berikut adalah beberapa informasi relevan dari web terkait pertanyaan pengguna, gunakan ini sebagai referensi utama tapi crosscheck kebenarannya dengan pengetahuan umum kamu:\n\n"
            f"{summary}\n\n"
            f"Berdasarkan informasi tersebut, improve dan jawab pertanyaan berikut dengan 100% sesuai konteks: kalau ada yang gak akurat di summary, koreksi dengan info yang bener, jangan tambah-tambah yang gak relevan, dan selalu fokus ke wisata Lelana.id: \"{user_query}\". "
            f"Kalau info dari web kurang lengkap, tambahin dari pengetahuanmu tapi bilang sumbernya jujur ya!"
        )

    answer = call_gemini(prompt)

    if answer is None:
        return "Maaf, sepertinya Putri sedang mengalami sedikit kendala teknis. Coba lagi beberapa saat lagi ya! 😢"
    
    return answer.strip()