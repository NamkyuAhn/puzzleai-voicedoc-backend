from datetime import date, datetime

from users.models        import Subject, Doctor, User, Hospital, DoctorDay, DoctorTime
from reservations.models import Reservation, ReservationImage, Status
from voicedoc.settings   import IP_ADDRESS
from core.functions      import jwt_generator, convertor

from django.test import TestCase, TransactionTestCase, Client
from django.db.models.functions import Concat
from django.db.models           import CharField, Value, Q

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
                       time = '10:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '11:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '12:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '13:00',
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
        reservations  = Reservation.objects.filter(Q(doctor_id = doctor.id, date = full_date, status_id = 1) #취소된 예약의 시간은 불러오지않게
                                                 | Q(doctor_id = doctor.id, date = full_date, status_id = 2))          
        working_times = DoctorTime.objects.filter(days = full_date.weekday())
        time_list     = [time.time.strftime("%H:%M") for time in working_times]
        expired_time  = [reservation.time.strftime("%H:%M") for reservation in reservations]

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

class ReservationDetailAndCancelTest(TestCase):
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
            User(name = '환자2', 
                 email = 'patient2@gmail.com',
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

        patient  = User.objects.get(name='환자1')
        doc      = User.objects.get(name = '의사1')
        hospital = Hospital.objects.get(name = '병원1')
        subject  = Subject.objects.get(name = '과목1')
        
        Doctor.objects.create(
            user_id = doc.id,
            profile_image = 'image',
            hospital_id = hospital.id,
            subject_id = subject.id,
        )

        doctor = Doctor.objects.get(hospital_id = hospital.id)

        Status.objects.bulk_create([
            Status(name = '진료대기'),
            Status(name = '진료완료'),
            Status(name = '진료취소')
        ])

        status     = Status.objects.get(name='진료대기')
        end_status = Status.objects.get(name='진료완료')
        canceled   = Status.objects.get(name='진료취소')

        Reservation.objects.bulk_create([
            Reservation(symtom = 'good',
                        opinion = 'ddd',
                        date = full_date,
                        time = '12:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = status.id,
                        user_id = User.objects.get(name='환자1').id),

            Reservation(symtom = 'ended',
                        opinion = 'ddd',
                        date = full_date,
                        time = '13:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = end_status.id,
                        user_id = patient.id),

            Reservation(symtom = 'canceld',
                        opinion = 'ddd',
                        date = full_date,
                        time = '14:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = canceled.id,
                        user_id = User.objects.get(name='환자1').id),

            Reservation(symtom = 'other user',
                        opinion = 'ddd',
                        date = full_date,
                        time = '13:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = status.id,
                        user_id = User.objects.get(name='환자2').id),
        ])
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_detail_load_success(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}

        reservation = Reservation.objects.get(symtom = 'good')
        response  = client.get(f'/reservations?res_id={reservation.id}', **header)
        images = ReservationImage.objects.filter(reservation_id = reservation.id)\
                .annotate(
                 url = Concat(Value(IP_ADDRESS), 'image', output_field = CharField()),
                 )

        image_list = []
        for image in images:
            image_list.append({
                'url' : image.url,
                'id' : image.id
            })

        result = {'status' :  reservation.status.name,
            'image' : image_list,
            'symptom' : reservation.symtom,
            'doctorOpinion' : reservation.opinion,
            'reservationDate' : convertor(reservation.date, reservation.time)
            }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result' : result})

    def test_detail_load_fail(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}
        other_user = User.objects.get(name='환자2')
        reservation = Reservation.objects.get(user_id = other_user.id)
        response  = client.get(f'/reservations?res_id={reservation.id}', **header)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'message' : 'not allowed'})

    def test_detail_cancel_success(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        status      = Status.objects.get(name = '진료대기')
        reservation = Reservation.objects.get(user_id = user.id, status_id = status.id)
        response    = client.patch(f'/reservations?res_id={reservation.id}&work=cancel', **header)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message' : 'canceled'})
    
    def test_detail_cancel_fail_other_patient(self):
        client    = Client()
        user      = User.objects.get(name='환자1')
        token     = jwt_generator(user.id)
        header    = {'HTTP_Authorization' : token}
        other_user = User.objects.get(name='환자2')
        reservation = Reservation.objects.get(user_id = other_user.id)
        response  = client.patch(f'/reservations?res_id={reservation.id}&work=cancel', **header)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'message' : 'not allowed'})
    
    def test_detail_cancel_fail_ended_reservation(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        status      = Status.objects.get(name='진료완료')
        reservation = Reservation.objects.get(status_id = status.id)
        response    = client.patch(f'/reservations?res_id={reservation.id}&work=cancel', **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'already ended or canceled'})

    def test_detail_cancel_fail_canceled_reservation(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        status      = Status.objects.get(name='진료취소')
        reservation = Reservation.objects.get(status_id = status.id)
        response    = client.patch(f'/reservations?res_id={reservation.id}&work=cancel', **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'already ended or canceled'})

class ReservationCreateTest(TransactionTestCase):
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
            User(name = '환자2', 
                 email = 'patient2@gmail.com',
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

        doc      = User.objects.get(name = '의사1')
        hospital = Hospital.objects.get(name = '병원1')
        subject  = Subject.objects.get(name = '과목1')
        
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
                       time = '11:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '12:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '13:00',
                       doctor_id = doctor.id),
            DoctorTime(days = testday.weekday(),
                       time = '14:00',
                       doctor_id = doctor.id),
        ])

        Status.objects.bulk_create([
            Status(name = '진료대기'),
            Status(name = '진료완료'),
            Status(name = '진료취소')
        ])

        status   = Status.objects.get(name='진료대기')
        ended    = Status.objects.get(name='진료완료')
        canceled = Status.objects.get(name='진료취소')

        Reservation.objects.bulk_create([
            Reservation(symtom = 'good',
                        opinion = 'ddd',
                        date = full_date,
                        time = '12:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = ended.id,
                        user_id = User.objects.get(name='환자2').id),

            Reservation(symtom = 'ended',
                        opinion = 'ddd',
                        date = full_date,
                        time = '13:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = status.id,
                        user_id = User.objects.get(name='환자2').id),

            Reservation(symtom = 'canceled',
                        opinion = 'ddd',
                        date = full_date,
                        time = '14:00:00.000000',
                        doctor_id = doctor.id,
                        status_id = canceled.id,
                        user_id = User.objects.get(name='환자1').id),
        ])

        ReservationImage.objects.bulk_create([
            ReservationImage(
                image = 'dd',
                reservation_id = Reservation.objects.get(symtom = 'good').id
            ),
            ReservationImage(
                image = 'dd',
                reservation_id = Reservation.objects.get(symtom = 'ended').id
            ),
            ReservationImage(
                image = 'dd',
                reservation_id = Reservation.objects.get(symtom = 'canceled').id
            ),
        ])

    def tearDown(self) -> None:
        return super().tearDown()
    
    # def test_create_success(self):
    #     client      = Client()
    #     user        = User.objects.get(name='환자1')
    #     token       = jwt_generator(user.id)
    #     header      = {'HTTP_Authorization' : token}
    #     doc         = User.objects.get(name = '의사1')
    #     testday     = datetime.now()
    #     year        = testday.year
    #     month       = testday.month
    #     day         = testday.day
    #     form        = {'doctor_id':doc.id,
    #                     'year':f'{year}',
    #                     'month':f'{month}',
    #                     'date':f'{day}',
    #                     'time':'11:00',
    #                     'symptom':'asdf',
    #                     'img':['ddd']}
    #     response    = client.post(f'/reservations', form, **header)

    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.json(), {'message' : 'reservation created'})
    
    # def test_create_success_on_cancel_time(self):
        # client      = Client()
        # user        = User.objects.get(name='환자1')
        # token       = jwt_generator(user.id)
        # header      = {'HTTP_Authorization' : token}
        # doc         = User.objects.get(name = '의사1').id
        # testday     = datetime.now()
        # year        = testday.year
        # month       = testday.month
        # day         = testday.day
        # form        = {
        #                 'doctor_id':Doctor.objects.get(user_id = doc).id,
        #                 'year':f'{year}',
        #                 'month':f'{month}',
        #                 'date':f'{day}',
        #                 'time':'14:00',
        #                 'symptom':'asdf',
        #                 'img':['ddd']
        # }
        # response    = client.post(f'/reservations', form, **header)

        # self.assertEqual(response.status_code, 201)
        # self.assertEqual(response.json(), {'message' : 'reservation created'})
    
    def test_create_fail_workingtime(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        doc         = User.objects.get(name = '의사1').id
        testday     = datetime.now()
        year        = testday.year
        month       = testday.month
        day         = testday.day
        form        = {
                        'doctor_id':Doctor.objects.get(user_id = doc).id,
                        'year':f'{year}',
                        'month':f'{month}',
                        'date':f'{day}',
                        'time':'09:00',
                        'symptom':'asdf',
                        'img':['ddd']
        }
        response    = client.post(f'/reservations', form, **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not working time'})
    
    def test_create_fail_workingday(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        doc         = User.objects.get(name = '의사1').id
        testday     = datetime.now()
        year        = testday.year
        month       = testday.month
        day         = testday.day+1
        form        = {
                        'doctor_id':Doctor.objects.get(user_id = doc).id,
                        'year':f'{year}',
                        'month':f'{month}',
                        'date':f'{day}',
                        'time':'11:00',
                        'symptom':'asdf',
                        'img':['ddd']
        }
        response    = client.post(f'/reservations', form, **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not working day'})
    
    def test_create_fail_olddate(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        doc         = User.objects.get(name = '의사1').id
        testday     = datetime.now()
        year        = testday.year
        month       = testday.month
        day         = testday.day-1
        form        = {
                        'doctor_id':Doctor.objects.get(user_id = doc).id,
                        'year':f'{year}',
                        'month':f'{month}',
                        'date':f'{day}',
                        'time':'11:00',
                        'symptom':'asdf',
                        'img':['ddd']
        }
        response    = client.post(f'/reservations', form, **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not allowed to make reservation to old date'})
    
    def test_create_fail_already_exist_1(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        doc         = User.objects.get(name = '의사1').id
        testday     = datetime.now()
        year        = testday.year
        month       = testday.month
        day         = testday.day-1
        form        = {
                        'doctor_id':Doctor.objects.get(user_id = doc).id,
                        'year':f'{year}',
                        'month':f'{month}',
                        'date':f'{day}',
                        'time':'12:00',
                        'symptom':'asdf',
                        'img':['ddd']
        }
        response    = client.post(f'/reservations', form, **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not allowed to make reservation to old date'})
    
    def test_create_fail_already_exist_2(self):
        client      = Client()
        user        = User.objects.get(name='환자1')
        token       = jwt_generator(user.id)
        header      = {'HTTP_Authorization' : token}
        doc         = User.objects.get(name = '의사1').id
        testday     = datetime.now()
        year        = testday.year
        month       = testday.month
        day         = testday.day-1
        form        = {
                        'doctor_id':Doctor.objects.get(user_id = doc).id,
                        'year':f'{year}',
                        'month':f'{month}',
                        'date':f'{day}',
                        'time':'13:00',
                        'symptom':'asdf',
                        'img':['ddd']
        }
        response    = client.post(f'/reservations', form, **header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'not allowed to make reservation to old date'})


