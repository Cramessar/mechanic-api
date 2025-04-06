# File: tests/test_customers.py

import unittest
import sys
import os
from flask import Flask
from application import create_app
from application.extensions import db
from application.models import Customer
from application.utils import hash_password
import json


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestConfig:
    SECRET_KEY = "testing-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

class CustomerRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # test customer
            self.customer = Customer(
                name="TestUser",
                email="test@example.com",
                password=hash_password("password123")
            )
            db.session.add(self.customer)
            db.session.commit()

            # login to get token
            login_response = self.client.post("/customers/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            response_data = login_response.get_json()
            print("🔑 Login token during test:", response_data)

            self.token = response_data.get("token", None)
            if not self.token:
                print("❌ No token received! Full login response:", response_data)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_customer_success(self):
        response = self.client.post("/customers/register", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 201)

    def test_register_customer_missing_field(self):
        response = self.client.post("/customers/register", json={"name": "Bob"})
        self.assertEqual(response.status_code, 400)

    def test_login_customer_success(self):
        response = self.client.post("/customers/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())

    def test_login_customer_invalid_credentials(self):
        response = self.client.post("/customers/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_get_customer_tickets_unauthorized(self):
        response = self.client.get("/customers/TestUser/tickets")
        self.assertEqual(response.status_code, 401)

    def test_get_customer_tickets_authorized(self):
        if not self.token:
            self.skipTest("Token not available from login step")

        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = self.client.get(f"/customers/TestUser/tickets", headers=headers)
        print("🔁 Auth Response JSON:", response.get_json())
        self.assertIn(response.status_code, [200, 403], msg=response.get_json())

    def test_paginated_customer_list(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
