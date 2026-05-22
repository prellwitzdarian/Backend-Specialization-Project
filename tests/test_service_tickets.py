import unittest
from app import create_app
from app.models import db, Customers, Mechanics, Inventory, Service_tickets
from app.utils.util import encode_token, encode_mechanic_token

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            cust = Customers(name='cust', email='cust@mail.com', phone='000', password='pw')
            mech = Mechanics(name='mech', email='mech@mail.com', phone='111', salary=10.0, password='pw')
            part = Inventory(name='part', price=3.3)
            db.session.add_all([cust, mech, part])
            db.session.commit()
            self.customer_id = cust.id
            self.mechanic_id = mech.id
            self.part_id = part.id
        self.client = self.app.test_client()
        self.cust_token = encode_token(self.customer_id)
        self.mech_token = encode_mechanic_token(self.mechanic_id)

    def test_create_service_ticket(self):
        payload = {'service_date': '2026-01-01', 'issue_description': 'brakes', 'vin': 'VIN1'}
        headers = {'Authorization': 'Bearer ' + self.cust_token}
        resp = self.client.post('/service-tickets/', json=payload, headers=headers)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json['issue_description'], 'brakes')
        ticket_id = resp.json['id']

        # assign mechanic
        headers_mech = {'Authorization': 'Bearer ' + self.mech_token}
        resp2 = self.client.put(f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}', headers=headers_mech)
        self.assertEqual(resp2.status_code, 200)

        # add part
        resp3 = self.client.put(f'/service-tickets/{ticket_id}/add-part/{self.part_id}', headers=headers_mech)
        self.assertEqual(resp3.status_code, 200)

    def test_get_and_edit_ticket(self):
        # create ticket directly
        with self.app.app_context():
            ticket = Service_tickets(customer_id=self.customer_id, service_date='2026-02-02', issue_description='a', vin='V2')
            db.session.add(ticket)
            db.session.commit()
            tid = ticket.id
        resp = self.client.get(f'/service-tickets/{tid}')
        self.assertEqual(resp.status_code, 200)
        # edit (no mechanics to add/remove) but should still succeed
        headers_mech = {'Authorization': 'Bearer ' + self.mech_token}
        resp2 = self.client.put(f'/service-tickets/{tid}/edit', json={'add_mechanic_ids': [], 'remove_mechanic_ids': []}, headers=headers_mech)
        self.assertEqual(resp2.status_code, 200)

if __name__ == '__main__':
    unittest.main()
