def test_create_itinerari_unauthenticated(client):
    """Menguji akses ke halaman pembuatan itinerari ketika pengguna belum login.

    Args:
        client: Klien pengujian yang tidak terautentikasi
    """
    response = client.get('/itinerari/buat', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_create_itinerari_authenticated(authenticated_client, wisata_fixture):
    """Menguji proses pembuatan itinerari baru yang sukses oleh pengguna terautentikasi.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi
        wisata_fixture: Fixture wisata untuk pengujian
    """
    wisata_ids = [str(w.id) for w in wisata_fixture]
    response = authenticated_client.post('/itinerari/buat', data={
        'judul': 'Itinerari Baru Saya',
        'deskripsi': 'Deskripsi untuk itinerari baru.',
        'wisata_termasuk': wisata_ids
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Itinerari Petualangan baru berhasil dibuat!" in response.data
    assert b"Itinerari Petualangan" in response.data


def test_edit_itinerari_by_owner(authenticated_client, itinerari_fixture):
    """Menguji kemampuan pemilik itinerari untuk mengakses halaman edit dan memproses pembaruan data.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi sebagai pemilik
        itinerari_fixture: Fixture itinerari untuk pengujian
    """
    response_get = authenticated_client.get(f'/itinerari/edit/{itinerari_fixture.id}')
    assert response_get.status_code == 200
    assert bytes(itinerari_fixture.judul, 'utf-8') in response_get.data

    response_post = authenticated_client.post(f'/itinerari/edit/{itinerari_fixture.id}', data={
        'judul': 'Judul Diperbarui',
        'deskripsi': itinerari_fixture.deskripsi,
        'wisata_termasuk': [str(w.id) for w in itinerari_fixture.wisata_termasuk]
    }, follow_redirects=True)

    assert response_post.status_code == 200
    assert b"Itinerari berhasil diperbarui!" in response_post.data
    assert b"Judul Diperbarui" in response_post.data


def test_edit_itinerari_by_non_owner_forbidden(client, auth, test_user2, itinerari_fixture):
    """Menguji pencegahan pengeditan itinerari oleh pengguna yang bukan pemilik.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        auth: Objek AuthActions untuk login
        test_user2: Fixture pengguna kedua untuk pengujian
        itinerari_fixture: Fixture itinerari untuk pengujian
    """
    auth.login(test_user2.email, 'TestPassword123!')
    response = client.get(f'/itinerari/edit/{itinerari_fixture.id}')
    assert response.status_code == 403


def test_delete_itinerari_by_owner(authenticated_client, itinerari_fixture):
    """Menguji kemampuan pemilik itinerari untuk menghapus itinerari dari sistem.

    Args:
        authenticated_client: Klien pengujian yang terautentikasi sebagai pemilik
        itinerari_fixture: Fixture itinerari untuk pengujian
    """
    response = authenticated_client.post(f'/itinerari/hapus/{itinerari_fixture.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Itinerari telah berhasil dihapus." in response.data


def test_delete_itinerari_by_non_owner_forbidden(client, auth, test_user2, itinerari_fixture):
    """Menguji pencegahan penghapusan itinerari oleh pengguna yang bukan pemilik.

    Args:
        client: Klien pengujian yang tidak terautentikasi
        auth: Objek AuthActions untuk login
        test_user2: Fixture pengguna kedua untuk pengujian
        itinerari_fixture: Fixture itinerari untuk pengujian
    """
    auth.login(test_user2.email, 'TestPassword123!')
    response = client.post(f'/itinerari/hapus/{itinerari_fixture.id}')
    assert response.status_code == 403