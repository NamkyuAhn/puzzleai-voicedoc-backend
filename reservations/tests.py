from users.models      import Subject, Doctor, User, Hospital
from voicedoc.settings import IP_ADDRESS, TEST_TOKEN
from core.functions    import jwt_generator

from django.test import TestCase , Client
from django.db.models.functions import Concat
from django.db.models           import CharField, Value

class SubjectAndDoctorLoadTest(TestCase):
    def setUp(self):
        User.objects.create(
            name = '의사 1',
            email = 'email@gmail.com',
            password = '1q2w3e4r',
            is_doctor = 'True'
        )
        Subject.objects.create(
            name  = "과목 1",
            image = "image 예시"
        )
        Hospital.objects.create(
            name = '병원 1'
        )
        user = User.objects.get(is_doctor = True)
        hospital = Hospital.objects.get(name = '병원 1')
        subject = Subject.objects.get(name = '과목 1')

        Doctor.objects.create(
            user_id = user.id,
            profile_image = 'image',
            working_days = 'days',
            working_times = 'times',
            hospital_id = hospital.id,
            subject_id = subject.id,
        )

    def tearDown(self):
        Subject.objects.all().delete()
        User.objects.all().delete()
        Doctor.objects.all().delete()
        Hospital.objects.all().delete()
    
    def test_subject_loading(self):
        client = Client()
        user = User.objects.get(name='의사 1')
        token = jwt_generator(user.id)
        header = {'HTTP_Authorization' : token}
        response = client.get('/reservations/subject', **header)

        subjects  = Subject.objects.annotate(
            file_location = Concat(
                Value(IP_ADDRESS), 'image', 
                    output_field = CharField()
                )
            )\
        .values('id', 'name', 'file_location')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : list(subjects)})

    def test_subject_doctor_loading(self):
        client = Client()
        user = User.objects.get(name='의사 1')
        token = jwt_generator(user.id)
        header = {'HTTP_Authorization' : token}
        response = client.get('/reservations/subject/1', **header)

        doctors = Doctor.objects.filter(subject_id = 1)\
        .select_related('subject', 'hospital', 'user')\
        .annotate(
            file_location = Concat(
                Value(IP_ADDRESS), 'profile_image', output_field = CharField()),
            name          = Concat('user__name', Value(''),output_field = CharField()),
            hospital_name = Concat('hospital__name', Value(''),output_field = CharField()),
            subject_name  = Concat('subject__name', Value(''),output_field = CharField()),
            )\
        .values('id', 'name', 'file_location', 'hospital_name', 'subject_name')  

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : list(doctors)})