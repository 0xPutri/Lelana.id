from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.services.chatbot_handler import get_bot_response

chatbot = Blueprint('chatbot', __name__)

@chatbot.route('/chatbot')
@login_required
def chat_page():
    """Menampilkan halaman antarmuka chatbot untuk pengguna terautentikasi.

    Returns:
        Response: Render template halaman chatbot.
    """
    return render_template('chatbot/chat.html')

@chatbot.route('/api/chatbot/ask', methods=['POST'])
@login_required
def ask_putri():
    """Menangani permintaan API untuk mendapatkan respons dari chatbot.

    Menerima pertanyaan pengguna dalam format JSON, memvalidasi keberadaannya,
    lalu mengembalikan jawaban dari layanan chatbot.

    Returns:
        Response: JSON berisi respons chatbot jika sukses, atau pesan error jika input tidak valid.
    """
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({'error': 'Pertanyaan tidak boleh kosong.'}), 400

    bot_response = get_bot_response(user_query)
    
    return jsonify({'response': bot_response})