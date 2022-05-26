import json

from django.test  import Client, TransactionTestCase, TestCase
from users.models import User

class UserSignupTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            name      = 'test1',
            email     = 'test1@gmail.com',
            is_doctor = 'False',
            password  = '1q2w3e4r'
        )

    def tearDown(self):
        User.objects.all().delete()
    
    def test_signup_success(self):
        client = Client()
        form = {
            'name'      : 'test2',
            'email'     : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password'  : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message' : 'signup success'})

    def test_keyerror(self):
        client = Client()
        form = {
            'name'      : 'test2',
            'email'     : 'test2@gmail.com',
            'is_doctor' : 'False',
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KeyError'})

    def test_name_is_none(self):
        client = Client()
        form = {
            'name'      : '',
            'email'     : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password'  : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user name'})
    
    def test_is_doctor_is_none(self):
        client = Client()
        form = {
            'name'      : 'test2',
            'email'     : 'test2@gmail.com',
            'is_doctor' : '',
            'password'  : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'must have user is_doctor'})
    
    def test_email_validation_error(self):
        client = Client()
        form = {
            'name'      : 'test2',
            'email'     : 'test2gmail.com',
            'is_doctor' : 'False',
            'password'  : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not in email format'})
    
    def test_password_validation_error(self):
        client = Client()
        form = {
            'name'      : 'test2',
            'email'     : 'test2@gmail.com',
            'is_doctor' : 'False',
            'password'  : '1234'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not in password format'})

class UserSignupIntergrityErrorTest(TransactionTestCase):
    def setUp(self):
        User.objects.create_user(
            name      = 'test1',
            email     = 'test1@gmail.com',
            is_doctor = 'False',
            password  = '1q2w3e4r'
        )
    
    def tearDown(self):
        User.objects.all().delete()
    
    def test_email_already_exist(self):
        client = Client()
        form = {
            'name'      : 'test1',
            'email'     : 'test1@gmail.com',
            'is_doctor' : 'False',
            'password'  : '1q2w3e4r'
        }	
	    
        response = client.post('/users/signup', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'email is already exists'})

class UserValidationTest(TestCase):
    def test_email_validation_pass(self):
        client = Client()
        form = {'email' : 'test1@gmail.com'}

        response = client.post('/users/email_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message' : 'email validation pass'})

    def test_email_validation_error(self):
        client = Client()
        form = {'email' : 'test2gmail.com'}	
	    
        response = client.post('/users/email_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not in email format'})
    
    def test_email_validation_keyerror(self):
        client = Client()
        form = {}	
	    
        response = client.post('/users/email_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KeyError'})

    def test_password_validation_pass(self):
        client = Client()
        form = {'password' : '1q2w3e4r'}	
	    
        response = client.post('/users/password_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message' : 'password validation pass'})

    def test_password_validation_error(self):
        client = Client()
        form = {'password' : '1234'}	
	    
        response = client.post('/users/password_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not in password format'})

    def test_password_validation_keyerror(self):
        client = Client()
        form = {}	
	    
        response = client.post('/users/password_check', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KeyError'})

class UserSigninTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            name = 'patient',
            email = 'patient@gmail.com',
            is_doctor = 'False',
            password = '1q2w3e4r'
        )
        User.objects.create_user(
            name = 'doctor',
            email = 'doctor@gmail.com',
            is_doctor = 'True',
            password = '1q2w3e4r'
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_user_signin_success(self):
        client = Client()
        form = {'email' : 'patient@gmail.com', 'password' : '1q2w3e4r'}

        response = client.post('/users/signin', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message' : 'login success'})

    def test_user_signin_fail(self):
        client = Client()
        form = {'email' : 'patient@gmail.com', 'password' : 'asdf1234'}

        response = client.post('/users/signin', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'check email or password'})

    def test_doctor_login(self):
        client = Client()
        form = {'email' : 'doctor@gmail.com', 'password' : '1q2w3e4r'}

        response = client.post('/users/signin', json.dumps(form), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'please login on app for doctor'})