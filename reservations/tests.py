from django.test import TestCase , Client
from users.models import Subject, Doctor, User, Hospital

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
        user = User.objects.get(is_doctor = 'True')
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
        response = client.get('/reservations/subject')
        subjects  = Subject.objects.all().prefetch_related("doctor_set")
        result = []

        for subject in subjects:
            file_location = '192.168.0.114:8000/media/' + str(subject.image)
            result.append({
                "subject_id" : subject.id,
                "subject_name" : subject.name,
                "subject_iamge" : file_location
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : result})

    def test_subject_doctor_loading(self):
        client = Client()
        response = client.get('/reservations/subject/1')
        doctor = Doctor.objects.get(user_id = 1)

        file_location = '192.168.0.114:8000/media/' + str(doctor.profile_image)
        result = [{
            "name" : doctor.user.name,
            "subject" : doctor.subject.name,
            "hospital" : doctor.hospital.name,
            "profile_image" : file_location
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : result})