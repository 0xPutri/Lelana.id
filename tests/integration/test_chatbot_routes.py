import pytest


def test_chat_page_get_request(client):
    """Menguji [GET /chatbot] - Halaman antarmuka chat.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/chatbot')
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_ask_putri_unauthenticated(client):
    """Menguji [POST /api/chatbot/ask] - Endpoint API tanpa autentikasi.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.post('/api/chatbot/ask', json={'query': 'Halo'})
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_ask_putri_empty_input(authenticated_client):
    """Menguji skenario whitebox [POST /api/chatbot/ask] dengan input kosong.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
    """
    response = authenticated_client.post('/api/chatbot/ask', json={'query': ''})
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Pertanyaan tidak boleh kosong.'


def test_ask_putri_valid_input(authenticated_client, monkeypatch):
    """Menguji skenario whitebox [POST /api/chatbot/ask] dengan input valid.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        monkeypatch: Fixture pytest untuk menyuntikkan dependensi
    """
    monkeypatch.setattr(
        'app.routes.chatbot_routes.get_bot_response',
        lambda _: "Ini adalah respons tiruan."
    )

    response = authenticated_client.post('/api/chatbot/ask', json={'query': 'Halo'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'response' in json_data
    assert json_data['response'] == "Ini adalah respons tiruan."