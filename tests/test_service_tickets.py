# File: tests/test_service_tickets.py

import unittest
from application import create_app
from application.extensions import db
from application.models import Customer, Mechanic, ServiceTicket, Inventory
from application.utils import hash_password, encode_token


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


class ServiceTicketRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            self.customer = Customer(
    name="TicketTester",
    email="ticket@test.com",
    password=hash_password("pass123")
)

            self.mechanic = Mechanic(name="TicketFixer", password=hash_password("mechpass"))
            self.part = Inventory(name="Brake Pad", price=79.99)
            db.session.add_all([self.customer, self.mechanic, self.part])
            db.session.commit()

            self.customer_id = self.customer.id
            self.mechanic_id = self.mechanic.id
            self.part_id = self.part.id

            self.ticket = ServiceTicket(description="Test grinding noise", customer_id=self.customer_id)
            db.session.add(self.ticket)
            db.session.commit()

            self.ticket_id = self.ticket.id

            self.customer_token = encode_token(str(self.customer_id), role="customer")
            self.mechanic_token = encode_token(str(self.mechanic_id), role="mechanic")

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_ticket(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.post("/service-tickets/", json={"description": "Engine light on"}, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_list_all_tickets(self):
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)

    def test_get_my_tickets(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.get("/service-tickets/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_edit_mechanics_on_ticket(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.put(f"/service-tickets/{self.ticket_id}/edit", json={
            "add_ids": [self.mechanic_id]
        }, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("added", response.get_json())

    def test_add_parts_to_ticket(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.put(f"/service-tickets/{self.ticket_id}/add-part", json={
            "part_ids": [self.part_id]
        }, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_update_ticket_status(self):
        headers = {"Authorization": f"Bearer {self.mechanic_token}"}
        response = self.client.put(f"/service-tickets/{self.ticket_id}/update-status", json={
            "status": "Completed"
        }, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Status updated", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
