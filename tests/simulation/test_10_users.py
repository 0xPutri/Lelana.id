import pytest
from app import create_app, db
from app.models.user import User
from tests.helpers import AuthActions


@pytest.fixture(scope='module')
def app():
    """Fixture untuk membuat dan mengkonfigurasi aplikasi Flask untuk pengujian.

    Returns:
        Flask.app: Instance aplikasi Flask yang dikonfigurasi untuk pengujian
    """
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def client(app):
    """Fixture untuk menyediakan test client untuk aplikasi.

    Args:
        app: Instance aplikasi Flask dari fixture 'app'

    Returns:
        FlaskClient: Klien pengujian untuk membuat permintaan HTTP simulasi
    """
    return app.test_client()


class TestUserSimulation:
    """Mengelompokkan pengujian yang mensimulasikan interaksi beberapa pengguna."""

    def _run_single_user_simulation(self, app, user_id):
        """Menjalankan alur kerja simulasi yang benar untuk satu pengguna:
        Daftar -> Konfirmasi Manual -> Logout -> Login -> Verifikasi -> Logout.

        Args:
            app: Instance aplikasi Flask
            user_id: ID unik untuk pengguna simulasi

        Returns:
            str: Hasil dari simulasi untuk pengguna ini
        """
        with app.test_client() as client:
            username = f"user_sim_{user_id}"
            email = f"user_sim_{user_id}@lelana.my.id"
            password = "Password123!"

            print(f"\n--- Simulasi Pengguna {user_id}: {username} ---")

            auth = AuthActions(client)

            print(f"Pengguna {user_id}: Melakukan pendaftaran...")
            register_response = auth.register(username, email, password, password)
            if b'Logout' not in register_response.data:
                 print(f"Pengguna {user_id}: Pendaftaran GAGAL - tidak otomatis login.")
                 return f"Pengguna {user_id}: Gagal mendaftar"
            print(f"Pengguna {user_id}: Pendaftaran & login awal BERHASIL")

            with app.app_context():
                user = User.query.filter_by(email=email).first()
                if user and not user.is_confirmed:
                    user.is_confirmed = True
                    db.session.commit()
                    print(f"Pengguna {user_id}: Dikonfirmasi secara manual di DB.")

            print(f"Pengguna {user_id}: Logout untuk menyegarkan status sesi...")
            auth.logout()

            print(f"Pengguna {user_id}: Melakukan login kembali...")
            login_response = auth.login(email, password)
            if login_response.status_code != 200:
                print(f"Pengguna {user_id}: Login kembali GAGAL (status: {login_response.status_code})")
                return f"Pengguna {user_id}: Gagal login"
            print(f"Pengguna {user_id}: Login kembali BERHASIL.")

            print(f"Pengguna {user_id}: Memverifikasi akses ke profil...")
            response_profile = client.get('/profile')
            if response_profile.status_code == 200 and username.encode() in response_profile.data:
                print(f"Pengguna {user_id}: Akses profil BERHASIL")
            else:
                print(f"Pengguna {user_id}: GAGAL mengakses profil (status: {response_profile.status_code})")
                return f"Pengguna {user_id}: Gagal akses profil"

            print(f"Pengguna {user_id}: Melakukan logout terakhir...")
            auth.logout()

            response_after_logout = client.get('/profile')
            if response_after_logout.status_code != 302:
                print(f"Pengguna {user_id}: Logout terakhir GAGAL (masih bisa akses profil)")
                return f"Pengguna {user_id}: Gagal logout terakhir"

            return f"Pengguna {user_id}: SEMUA TES BERHASIL"

    def test_simulate_10_users(self, app):
        """Mensimulasikan 10 pengguna yang mendaftar, login, mengakses dasbor, dan logout.

        Args:
            app: Instance aplikasi Flask untuk menjalankan simulasi
        """
        results = []
        for i in range(1, 11):
            result = self._run_single_user_simulation(app, i)
            results.append(result)

        print("\n\n--- RINGKASAN SIMULASI ---")
        for res in results:
            print(res)

        assert len(results) == 10
        assert all("BERHASIL" in r for r in results)