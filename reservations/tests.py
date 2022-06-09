from datetime import date, datetime

from users.models        import Subject, Doctor, User, Hospital, DoctorDay, DoctorTime
from reservations.models import Reservation, Status
from voicedoc.settings   import IP_ADDRESS
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
            is_doctor = True
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
        testday   = datetime.now()
        year      = testday.year
        month     = testday.month
        day       = testday.day
        full_date = date(year, month, day)

        User.objects.bulk_create([
            User(name = '환자1', 
                 email = 'patient1@gmail.com',
                 password = '1q2w3e4r',
                 is_doctor = False),
            User(name = '의사1', 
                 email = 'doctor1@gmail.com',
                 password = '1q2w3e4r',
                 is_doctor = True)
        ])

        Subject.objects.create(
            name  = "과목1",
            image = "image 예시"
        )

        Hospital.objects.create(
            name = '병원1'
        )

        patient = User.objects.get(name='환자1')
        doc = User.objects.get(name = '의사1')
        hospital = Hospital.objects.get(name = '병원1')
        subject = Subject.objects.get(name = '과목1')
        
        Doctor.objects.create(
            user_id = doc.id,
            profile_image = 'image',
            hospital_id = hospital.id,
            subject_id = subject.id,
        )

        doctor = Doctor.objects.get(hospital_id = hospital.id)

        DoctorDay.objects.create(
            date = full_date,
            doctor_id = doctor.id,
        )

        DoctorTime.objects.bulk_create([
            DoctorTime(days = testday.weekday(),
                       times = '10:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       times = '11:00',
                       doctor_id = doctor.id),
        ])

        Status.objects.create(
            name = '진료대기'
        )

        status = Status.objects.get(name='진료대기')

        Reservation.objects.bulk_create([
            Reservation(symtom = 'asdf',
                        opinion = 'ddd',
                        date = full_date,
                        time = '12:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = status.id,
                        user_id = patient.id),
            Reservation(symtom = 'asdf',
                        opinion = 'ddd',
                        date = full_date,
                        time = '13:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = status.id,
                        user_id = patient.id)
        ])

    def tearDown(self) -> None:
        return super().tearDown()

    def test_workingday_loading_success(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}

        doc       = User.objects.get(name='의사1')
        doctor    = Doctor.objects.get(user_id = doc.id)
        testday   = datetime.now()
        year      = testday.year
        month     = testday.month
        day       = testday.day
        
        response  = client.get(f'/reservations/time/{doctor.id}?year={year}&month={month}', **header)

        days = DoctorDay.objects.filter(doctor_id = doctor.id)
        day_list = []
        for day in days:
            if day.date.month == month and day.date.year == year:
                day_list.append(day.date.weekday())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result" : list(set(day_list))})
    
    def test_workingtime_loading_success(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}

        doc       = User.objects.get(name='의사1')
        doctor    = Doctor.objects.get(user_id = doc.id)
        testday   = datetime.now()
        year      = testday.year
        month     = testday.month
        day       = testday.day

        response  = client.get(f'/reservations/time/{doctor.id}?year={year}&month={month}&dates={day}', **header)
        
        full_date     = date(year,month,day)
        reservations  = Reservation.objects.filter(doctor_id = doctor.id, date = full_date)
        working_times = DoctorTime.objects.filter(days = full_date.weekday())
        time_list     = [str(time.times) for time in working_times]
        expired_time  = [str(reservation.time)[:-3] for reservation in reservations]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'working_times' : time_list,
                                           'expired_times' : expired_time})

    def test_workingtime_loading_fail_oldtime(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}

        doc       = User.objects.get(name='의사1')
        doctor    = Doctor.objects.get(user_id = doc.id)
        testday   = datetime.now()
        year      = testday.year
        month     = testday.month
        day       = testday.day

        response  = client.get(f'/reservations/time/{doctor.id}?year={year}&month={month}&dates={day-1}', **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : "you can't read old calaneder"})

    def test_workingtime_loading_fail_notworkingday(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}

        doc       = User.objects.get(name='의사1')
        doctor    = Doctor.objects.get(user_id = doc.id)
        testday   = datetime.now()
        year      = testday.year
        month     = testday.month
        day       = testday.day
        full_date = date(year, month, day+1)
        response  = client.get(f'/reservations/time/{doctor.id}?year={year}&month={month}&dates={day+1}', **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : f'not work on {full_date}'})