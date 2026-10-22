import sys
import unittest
from app import app
import database as db

class AlgoPlayTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Algo", response.data)
        self.assertIn(b"Play", response.data)

    def test_auth_page(self):
        response = self.client.get("/auth")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Kirish", response.data)

    def test_learn_page(self):
        response = self.client.get("/learn")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Python Asoslari", response.data)
        self.assertIn(b"Algoritmlar", response.data)

    def test_games_page(self):
        response = self.client.get("/games")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Quiz Arena", response.data)
        self.assertIn(b"Kod Puzzle", response.data)

    def test_admin_protection(self):
        # Admin bo'lmagan foydalanuvchi /admin ga kirsa, login sahifasiga redirect bo'lishi kerak
        response = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_user_flow(self):
        # Register test
        import random
        rand_num = random.randint(10000, 99999)
        username = f"testuser_{rand_num}"
        phone = f"+99890{rand_num}"

        res = self.client.post("/api/auth/register", json={
            "phone": phone,
            "username": username,
            "password": "password123"
        })
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])

        # Login test (chunki ro'yxatdan o'tgandan so'ng avtomatik kirilmaydi)
        login_res = self.client.post("/api/auth/login", json={
            "phone_or_user": username,
            "password": "password123"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.get_json()["success"])

        # Save score
        score_res = self.client.post("/api/game/save-score", json={
            "game_type": "quiz",
            "score": 15,
            "xp_earned": 15,
            "details": "Test quiz solved"
        })
        self.assertEqual(score_res.status_code, 200)
        self.assertTrue(score_res.get_json()["success"])

    def test_admin_flow(self):
        # Admin login
        res = self.client.post("/admin/login", data={
            "username": "admin",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertIn(b"Admin login yoki paroli noto", res.data)

        # Correct admin login
        res2 = self.client.post("/admin/login", data={
            "username": "admin",
            "password": "admin777"
        }, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"AlgoPlay Boshqaruv Tizimi", res2.data)

if __name__ == "__main__":
    unittest.main()
