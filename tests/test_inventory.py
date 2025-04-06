# File: tests/test_inventory.py

import unittest
from application import create_app, db
from application.models import Inventory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seed import seed_db



class InventoryRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            seed_db(self.app)

        login_res = self.client.post("/mechanics/login", json={
            "name": "Mike",
            "password": "mechpass1"
        })

        print("🧪 Mechanic Login Response JSON:", login_res.get_json())

        self.token = login_res.get_json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_list_inventory(self):
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Brake Pad", response.data)

    def test_create_inventory_item(self):
        response = self.client.post("/inventory/", json={
            "name": "Oil Filter",
            "price": 14.99
        }, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Oil Filter", response.data)

    def test_update_inventory_item(self):
        with self.app.app_context():
            item = Inventory.query.first()
        response = self.client.put(f"/inventory/{item.id}", json={
            "name": "Premium Brake Pad",
            "price": 39.99
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Premium Brake Pad", response.data)

    def test_delete_inventory_item(self):
        with self.app.app_context():
            item = Inventory.query.first()
        response = self.client.delete(f"/inventory/{item.id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"deleted", response.data.lower())

    def test_create_inventory_item_missing_price(self):
        response = self.client.post("/inventory/", json={
        "name": "Incomplete Part"  # obligatory negative test as requested.
        }, headers=self.headers)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing", response.data)

if __name__ == "__main__":
    unittest.main()
