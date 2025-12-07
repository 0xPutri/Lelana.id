def test_get_index_page(client):
    """Menguji akses ke halaman beranda utama (index page) aplikasi Lelana.id.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Selamat Datang di Lelana.id' in response.data


def test_get_peta_wisata_page(client):
    """Menguji akses ke halaman yang menampilkan peta interaktif destinasi wisata.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/peta-wisata')
    assert response.status_code == 200
    assert b"Peta Wisata Interaktif" in response.data


def test_get_profile_page_unauthenticated(client):
    """Menguji akses ke halaman profil ketika pengguna belum terautentikasi (sebelum login).

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/profile', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Profil Saya" not in response.data


def test_get_profile_page_authenticated(authenticated_client, test_user):
    """Menguji akses ke halaman profil ketika pengguna telah berhasil terautentikasi.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        test_user: Fixture pengguna untuk pengujian
    """
    user, _ = test_user
    response = authenticated_client.get('/profile')

    assert response.status_code == 200
    assert b"Profil Saya" in response.data
    assert bytes(user.username, 'utf-8') in response.data


def test_get_chatbot_page_unauthenticated(client):
    """Menguji akses ke halaman chatbot ketika pengguna belum login.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/chatbot', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Tanya Putri - Lelana.id" not in response.data


def test_get_chatbot_page_authenticated(authenticated_client):
    """Menguji akses ke halaman chatbot setelah pengguna berhasil login.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
    """
    response = authenticated_client.get('/chatbot')
    assert response.status_code == 200
    assert b"Tanya Putri - Lelana.id" in response.data


def test_search_functionality(client, wisata_fixture):
    """Menguji fungsionalitas pencarian di seluruh situs.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_item = wisata_fixture[0]
    search_query = wisata_item.nama
    response = client.get(f'/search?q={search_query}')

    assert response.status_code == 200
    assert f'Hasil Pencarian untuk "{search_query}"'.encode() in response.data
    assert wisata_item.nama.encode() in response.data


def test_search_with_empty_query(client):
    """Menguji fungsionalitas pencarian dengan query kosong.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/search?q=')
    assert response.status_code == 200
    assert b'Tidak ada hasil ditemukan' in response.data


def test_search_with_no_results(client):
    """Menguji fungsionalitas pencarian yang tidak menghasilkan apa-apa.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    search_query = "asdfghjklzxcvbnm"
    response = client.get(f'/search?q={search_query}')
    assert response.status_code == 200
    assert b'Tidak ada hasil ditemukan' in response.data


def test_get_static_pages(client):
    """Menguji akses ke halaman-halaman statis.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    pages = {
        '/about': b'Membangun Jembatan Digital',
        '/contact': b'Kirim Pesan via WhatsApp',
        '/privacy': b'Privasi pengguna merupakan prioritas utama'
    }
    for page, expected_text in pages.items():
        response = client.get(page)
        assert response.status_code == 200
        assert expected_text in response.data