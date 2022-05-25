import json

from django.test  import Client, TransactionTestCase
from users.models import User

class UserSignupTest(TransactionTestCase):
    def setUp(self):
        User.objects.create_user(
            name = 'test1',
            email = 'test1@gmail.com',
            is_doctor = 'False',
            password = '1q2w3e4r'
        )

    def tearDown(self):
        User.objects.all().delete()
    
    def test_signup_success(self):
        client = Client()
        form = {
            'name'  : 'test2',
            'email' : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password' : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message' : 'signup success'})
    
    def test_email_already_exist(self):
        client = Client()
        form = {
            'name'  : 'test1',
            'email' : 'test1@gmail.com',
            'is_doctor' : 'False',
            'password' : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'email is already exists'})

    def test_keyerror(self):
        client = Client()
        form = {
            'name'  : 'test2',
            'email' : 'test2@gmail.com',
            'is_doctor' : 'False',
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KeyError'})

    def test_name_is_none(self):
        client = Client()
        form = {
            'name'  : '',
            'email' : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password' : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user name'})
    
    def test_email_is_none(self):
        client = Client()
        form = {
            'name'  : 'test2',
            'email' : '',
            'is_doctor' : 'False',
            'password' : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user email'})
    
    def test_is_doctor_is_none(self):
        client = Client()
        form = {
            'name'  : 'test2',
            'email' : 'test2@gmail.com',
            'is_doctor' : '',
            'password' : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user is_doctor'})
    
    def test_password_is_none(self):
        client = Client()
        form = {
            'name'  : 'test2',
            'email' : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password' : ''
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user password'})