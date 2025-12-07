import pytest
from unittest.mock import patch, MagicMock
from app.services.chatbot_handler import get_bot_response, search_web, call_gemini
import requests


@patch('app.services.chatbot_handler.call_gemini')
@patch('app.services.chatbot_handler.search_web')
def test_get_bot_response_with_web_results(mock_search_web, mock_call_gemini, app):
    """Menguji fungsi `get_bot_response` ketika pencarian web (grounding) berhasil mendapatkan hasil.

    Args:
        mock_search_web: Mock untuk fungsi search_web
        mock_call_gemini: Mock untuk fungsi call_gemini
        app: Instance aplikasi Flask
    """
    with app.app_context():
        mock_search_web.return_value = [
            {'title': 'Judul Hasil 1', 'snippet': 'Cuplikan hasil 1.'},
            {'title': 'Judul Hasil 2', 'snippet': 'Cuplikan hasil 2.'}
        ]
        mock_call_gemini.return_value = "   Jawaban dari Gemini.   "

        user_query = "rekomendasi wisata di Bandung"
        response = get_bot_response(user_query)

        mock_search_web.assert_called_once_with(user_query)
        mock_call_gemini.assert_called_once()

        prompt_arg = mock_call_gemini.call_args[0][0]
        assert "Berikut adalah beberapa informasi relevan dari web" in prompt_arg
        assert "- Judul Hasil 1: Cuplikan hasil 1." in prompt_arg
        assert user_query in prompt_arg

        assert response == "Jawaban dari Gemini."


@patch('app.services.chatbot_handler.call_gemini')
@patch('app.services.chatbot_handler.search_web')
def test_get_bot_response_without_web_results(mock_search_web, mock_call_gemini, app):
    """Menguji fungsi `get_bot_response` ketika pencarian web tidak mengembalikan hasil (fallback).

    Args:
        mock_search_web: Mock untuk fungsi search_web
        mock_call_gemini: Mock untuk fungsi call_gemini
        app: Instance aplikasi Flask
    """
    with app.app_context():
        mock_search_web.return_value = []
        mock_call_gemini.return_value = "Jawaban fallback."

        user_query = "pertanyaan tidak jelas"
        get_bot_response(user_query)

        mock_search_web.assert_called_once_with(user_query)
        mock_call_gemini.assert_called_once()

        prompt_arg = mock_call_gemini.call_args[0][0]
        assert "Berikut adalah beberapa informasi relevan dari web" not in prompt_arg
        assert "berdasarkan pengetahuan umum kamu" in prompt_arg
        assert user_query in prompt_arg


@patch('app.services.chatbot_handler.call_gemini')
@patch('app.services.chatbot_handler.search_web')
def test_get_bot_response_gemini_fails(mock_search_web, mock_call_gemini, app):
    """Menguji penanganan kegagalan ketika pemanggilan model Gemini mengembalikan nilai None.

    Args:
        mock_search_web: Mock untuk fungsi search_web
        mock_call_gemini: Mock untuk fungsi call_gemini
        app: Instance aplikasi Flask
    """
    with app.app_context():
        mock_search_web.return_value = []
        mock_call_gemini.return_value = None

        response = get_bot_response("apapun")
        assert response == "Maaf, sepertinya Putri sedang mengalami sedikit kendala teknis. Coba lagi beberapa saat lagi ya! 😢"


@patch('app.services.chatbot_handler.call_gemini')
@patch('app.services.chatbot_handler.search_web')
def test_get_bot_response_skip_search_flag(mock_search_web, mock_call_gemini, app):
    """Menguji fungsi `get_bot_response` ketika flag `./skip` digunakan untuk melewati pencarian web.

    Args:
        mock_search_web: Mock untuk fungsi search_web
        mock_call_gemini: Mock untuk fungsi call_gemini
        app: Instance aplikasi Flask
    """
    with app.app_context():
        mock_call_gemini.return_value = "Jawaban tanpa pencarian."

        user_query = "./skip halo putri"
        response = get_bot_response(user_query)

        mock_search_web.assert_not_called()
        mock_call_gemini.assert_called_once()

        prompt_arg = mock_call_gemini.call_args[0][0]
        assert "halo putri" in prompt_arg
        assert "./skip" not in prompt_arg
        assert "berdasarkan pengetahuan umum kamu" in prompt_arg

        assert response == "Jawaban tanpa pencarian."


def test_search_web_no_api_key(app):
    """Menguji cabang logika `search_web` ketika SERPER_API_KEY tidak dikonfigurasi.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        app.config['SERPER_API_KEY'] = None
        with patch.object(app.logger, 'error') as mock_logger:
            result = search_web("test query")
            assert result == []
            mock_logger.assert_called_once_with("Kunci API Serper belum dikonfigurasi.")


@patch('app.services.chatbot_handler.requests.post')
def test_search_web_request_exception(mock_post, app):
    """Menguji blok `except` pada `search_web` ketika terjadi error jaringan.

    Args:
        mock_post: Mock untuk fungsi requests.post
        app: Instance aplikasi Flask
    """
    with app.app_context():
        app.config['SERPER_API_KEY'] = 'kunci-rahasia'
        mock_post.side_effect = requests.exceptions.RequestException("Test network error")
        with patch.object(app.logger, 'error') as mock_logger:
            result = search_web("test query")
            assert result == []
            mock_logger.assert_called_once_with("Error saat mencari di Serper: Test network error")


def test_call_gemini_no_api_key(app):
    """Menguji cabang logika `call_gemini` ketika GEMINI_API_KEY tidak ada.

    Args:
        app: Instance aplikasi Flask
    """
    with app.app_context():
        app.config['GEMINI_API_KEY'] = None
        result = call_gemini("test prompt")
        assert result == "Error: Kunci API Gemini belum dikonfigurasi."


@patch('app.services.chatbot_handler.requests.post')
def test_call_gemini_request_exception(mock_post, app):
    """Menguji blok `except` pada `call_gemini` ketika terjadi error jaringan.

    Args:
        mock_post: Mock untuk fungsi requests.post
        app: Instance aplikasi Flask
    """
    with app.app_context():
        app.config['GEMINI_API_KEY'] = 'kunci-rahasia'
        mock_post.side_effect = requests.exceptions.RequestException("Test network error")
        with patch.object(app.logger, 'error') as mock_logger:
            result = call_gemini("test prompt")
            assert result is None
            mock_logger.assert_called_once()