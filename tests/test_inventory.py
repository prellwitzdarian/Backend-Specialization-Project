import unittest
from app import create_app
from app.models import db, Inventory, Mechanics
from app.utils.util import encode_mechanic_token

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            mech = Mechanics(name='mech', email='mech@email.com', phone='111', salary=10.0, password='pw')
            db.session.add(mech)
            db.session.commit()
            self.mechanic_id = mech.id
        self.client = self.app.test_client()
        self.token = encode_mechanic_token(self.mechanic_id)

    def test_create_inventory_part(self):
        payload = {'name': 'Part A', 'price': 9.99}
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.post('/inventory/', json=payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Part A')

    def test_get_inventory_list_and_item(self):
        # add a part
        with self.app.app_context():
            part = Inventory(name='Part B', price=5.0)
            db.session.add(part)
            db.session.commit()
            pid = part.id
        resp = self.client.get('/inventory/')
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.get(f'/inventory/{pid}')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json['name'], 'Part B')

    def test_update_and_delete_part(self):
        with self.app.app_context():
            part = Inventory(name='ToUpdate', price=1.0)
            db.session.add(part)
            db.session.commit()
            pid = part.id
        headers = {'Authorization': 'Bearer ' + self.token}
        upd = {'name': 'Updated', 'price': 2.0}
        resp = self.client.put(f'/inventory/{pid}', json=upd, headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], 'Updated')
        resp2 = self.client.delete(f'/inventory/{pid}', headers=headers)
        self.assertEqual(resp2.status_code, 200)

if __name__ == '__main__':
    unittest.main()
