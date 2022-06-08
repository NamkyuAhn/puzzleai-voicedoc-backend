from datetime import date

from users.models        import Subject, Doctor, User, Hospital, DoctorDay, DoctorTime
from reservations.models import Reservation
from voicedoc.settings   import IP_ADDRESS, TEST_TOKEN
from core.functions      import jwt_generator

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
        self.assertEqual(response.json(), {"result" : list(subjects), "name" : "의사 1"})

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

class DateAndTimeLoadTest(TestCase):
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
            hospital_id = hospital.id,
            subject_id = subject.id,
        )
        doctor = Doctor.objects.get(profile_image = 'image')

        DoctorDay.objects.create(
            days = '0,2,4',
            doctor_id = doctor.id,
            month = '6',
            year = '2022'
        )
        DoctorTime.objects.create(
            days = 2,
            times = '10:00,11:00,12:00,13:00,14:00,15:00,16:00',
            doctor_id = doctor.id
        )
    def tearDown(self) -> None:
        return super().tearDown()

    def test_workingday_loading_success(self):
        client = Client()
        token = TEST_TOKEN
        header = {'HTTP_Authorization' : token}
        response = client.get('/reservations/time/1?year=2022&month=6', **header)

        working_day = DoctorDay.objects.get(doctor_id = 1, 
                                    year = '2022', month = '6').days
        time_lists = working_day.split(",")
        result = []
        for time in time_lists:
            result.append(int(time))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : result})
    
    # def test_workingday_loading_fail(self):
    #     client = Client()
    #     token = TEST_TOKEN
    #     header = {'HTTP_Authorization' : token}
    #     response = client.get('/reservations/time/1?year=2022&month=6', **header)

    #     working_day = DoctorDay.objects.get(doctor_id = 1, 
    #                                 year = '2022', month = '9').days
    #     time_lists = working_day.split(",")
    #     result = []
    #     for time in time_lists:
    #         result.append(int(time))
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), {'message' : '조건에 부합하는 의사 근무날짜 없음'})
    
    def test_workingtime_loading_success(self):
        client = Client()
        token = TEST_TOKEN
        header = {'HTTP_Authorization' : token}
        response = client.get('/reservations/time/1?year=2022&month=6&dates=8', **header)
        full_day = '2022-6-8'
        reservations = Reservation.objects.filter(doctor_id = 1, date = full_day)
        day = date(2022, 6, 8).weekday()
        working_time = DoctorTime.objects.get(days = day).times
        time_list = working_time.split(',')
        working_times = {'times' : time_list}
        expired_time = [reservation.time for reservation in reservations]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'working_times' : working_times,
                                           'expired_times' : expired_time})
        
