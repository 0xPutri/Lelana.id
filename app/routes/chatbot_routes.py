from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.services.chatbot_handler import get_bot_response

# Membuat Blueprint untuk rute-rute terkait chatbot
chatbot = Blueprint('chatbot', __name__)

@chatbot.route('/chatbot')
@login_required
def chat_page():
    """Menampilkan halaman antarmuka chatbot.

    Halaman ini hanya dapat diakses oleh pengguna yang sudah login.

    Returns:
        Response: Render template halaman chat.
    """
    # Merender dan mengembalikan halaman HTML untuk antarmuka chat
    return render_template('chatbot/chat.html')

@chatbot.route('/api/chatbot/ask', methods=['POST'])
@login_required
def ask_putri():
    """Endpoint API untuk menerima dan merespons pertanyaan ke chatbot.

    Menerima pertanyaan pengguna dalam format JSON, memanggil layanan chatbot
    untuk mendapatkan jawaban, dan mengembalikannya dalam format JSON.

    Returns:
        Response: Objek JSON berisi jawaban dari chatbot atau pesan error.
    """
    # Mengambil data JSON dari body permintaan
    data = request.get_json()
    # Mendapatkan nilai dari kunci 'query'
    user_query = data.get('query')

    # Memvalidasi apakah pertanyaan dari pengguna ada dan tidak kosong
    if not user_query:
        # Mengembalikan respons error jika tidak ada pertanyaan
        return jsonify({'error': 'Pertanyaan tidak boleh kosong.'}), 400

    # Memanggil fungsi dari service layer untuk mendapatkan respons bot
    bot_response = get_bot_response(user_query)
    
    # Mengembalikan respons dari bot dalam format JSON
    return jsonify({'response': bot_response})
