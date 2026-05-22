import unittest
from app import create_app
from app.models import db, Mechanics
from app.utils.util import encode_mechanic_token

class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            mech = Mechanics(name='mech', email='mech@email.com', phone='111-222-3333', salary=50.0, password='pw')
            db.session.add(mech)
            db.session.commit()
            self.mechanic_id = mech.id
        self.client = self.app.test_client()
        self.token = encode_mechanic_token(self.mechanic_id)

    def test_create_mechanic(self):
        payload = {'name': 'New Mech', 'email': 'new@mail.com', 'phone': '000-000-0000', 'salary': 60.0, 'password': '123'}
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'New Mech')

    def test_get_mechanics_list(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('mechanics', response.json)

    def test_mechanic_login(self):
        creds = {'email': 'mech@email.com', 'password': 'pw'}
        response = self.client.post('/mechanics/login', json=creds)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_update_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        payload = {'name': 'Updated Mech'}
        response = self.client.put(f'/mechanics/{self.mechanic_id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Mech')

    def test_delete_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.delete(f'/mechanics/{self.mechanic_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted successfully', response.json['message'])

    def test_search_and_popular(self):
        response = self.client.get('/mechanics/search?name=mech')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
