# File: tests/test_mechanics.py

import unittest
from flask import Flask
from application import create_app
from application.extensions import db
from application.models import Mechanic
from application.utils import hash_password, encode_token
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


class MechanicRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            self.mechanic = Mechanic(
                name="TestMechanic",
                password=hash_password("secure123")
            )
            db.session.add(self.mechanic)
            db.session.commit()
            self.mechanic_id = self.mechanic.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_mechanic_success(self):
        response = self.client.post("/mechanics/register", json={
            "name": "NewMechanic",
            "password": "newpass"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("Mechanic registered successfully", response.get_data(as_text=True))

    def test_register_mechanic_duplicate(self):
        response = self.client.post("/mechanics/register", json={
            "name": "TestMechanic",
            "password": "anotherpass"
        })
        self.assertEqual(response.status_code, 409)

    def test_login_mechanic_success(self):
        response = self.client.post("/mechanics/login", json={
            "name": "TestMechanic",
            "password": "secure123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())

    def test_login_mechanic_invalid(self):
        response = self.client.post("/mechanics/login", json={
            "name": "TestMechanic",
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 401)

    def test_protected_mechanic_route_success(self):
        token = encode_token(user_id=str(self.mechanic_id), role="mechanic")
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/mechanics/protected", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("cleared for repairs", response.get_data(as_text=True))

    def test_protected_mechanic_route_unauthorized(self):
        headers = {"Authorization": "Bearer invalidtoken"}
        response = self.client.get("/mechanics/protected", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_list_all_mechanics(self):
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)


if __name__ == "__main__":
    unittest.main()
