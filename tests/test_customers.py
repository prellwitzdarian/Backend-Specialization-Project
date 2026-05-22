import unittest
from app import create_app
from app.models import db, Customers, Service_tickets
from app.utils.util import encode_token

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # create a test customer
            customer = Customers(name='test_user', email='test@email.com', phone='123-456-7890', password='test')
            db.session.add(customer)
            db.session.commit()
            self.customer_id = customer.id
        self.client = self.app.test_client()
        self.token = encode_token(self.customer_id)

    def test_create_customer(self):
        payload = {
            'name': 'John Doe',
            'email': 'jd@email.com',
            'phone': '555-555-5555',
            'password': '123'
        }
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')

    def test_invalid_creation_missing_email(self):
        payload = {
            'name': 'No Email',
            'phone': '000-000-0000',
            'password': '123'
        }
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)
        # marshmallow will report missing email
        self.assertIn('email', response.json)

    def test_login_customer(self):
        credentials = {'email': 'test@email.com', 'password': 'test'}
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('token', response.json)

    def test_invalid_login(self):
        credentials = {'email': 'bad@email.com', 'password': 'bad'}
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password.')

    def test_update_customer(self):
        payload = {'name': 'Updated'}
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.put(f'/customers/{self.customer_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated')

    def test_delete_customer(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.delete(f'/customers/{self.customer_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully deleted', response.json['message'])

    def test_get_my_tickets(self):
        # create a ticket for the test customer
        with self.app.app_context():
            ticket = Service_tickets(customer_id=self.customer_id, service_date='2026-01-01', issue_description='noise', vin='VIN123')
            db.session.add(ticket)
            db.session.commit()
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)


if __name__ == '__main__':
    unittest.main()
