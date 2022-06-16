from datetime import datetime, time

from reservations.models import Reservation, ReservationImage, Status
from users.models        import Subject, Doctor, DoctorDay, DoctorTime
from core.functions      import signin_decorator, convertor, patient_decorator
from voicedoc.settings   import IP_ADDRESS

from django.views import View
from django.http  import JsonResponse
from django.db    import transaction
from django.db.models.functions import Concat
from django.db.models           import CharField, Value, Q
from django.core.paginator      import Paginator

class SubjectView(View):
    @signin_decorator
    def get(self, request):
        subjects = Subject.objects.annotate(
            file_location = Concat(
                Value(IP_ADDRESS), 'image', 
                    output_field = CharField()
                )
            )\
        .values('id', 'name', 'file_location')        
        return JsonResponse({"result" : list(subjects), "name" : request.user.name}, status = 200)

class DoctorListView(View):
    @signin_decorator
    def get(self, request, subject_id):
        page   = int(request.GET.get('page', 1))
        limit  = int(request.GET.get('limit', 5))
        doctors = Doctor.objects.filter(subject_id = subject_id)\
        .select_related('subject', 'hospital', 'user')\
        .annotate(
            doctor_image  = Concat(Value(IP_ADDRESS), 'profile_image', output_field = CharField()),
            doctor_name   = Concat('user__name', Value(''),output_field = CharField()),
            hospital_name = Concat('hospital__name', Value(''),output_field = CharField()),
            subject_name  = Concat('subject__name', Value(''),output_field = CharField()),
            )\
        .values('id', 'doctor_name', 'hospital_name', 'subject_name', 'doctor_image')\
        .order_by('id')
        doctors = Paginator(doctors, limit)
        return JsonResponse({'result' : list(doctors.page(page).object_list)}, status = 200)

class DoctorWorkView(View):
    @signin_decorator
    def get(self, request, doctor_id):
        year   = int(request.GET.get('year'))
        month  = int(request.GET.get('month'))
        dates  = request.GET.get('dates', None)

        days     = DoctorDay.objects.filter(doctor_id = doctor_id)
        day_list = [day.date.weekday() for day in days 
                    if day.date.month == month and day.date.year == year]

        if dates != None: 
            full_date = datetime(int(year), int(month), int(dates))
            current   = datetime.now()
            
            if current.date() > full_date.date(): #과거시간 조회 못하게
                return JsonResponse({'message' : "you can't read old calaneder"}, status = 400)

            if full_date.weekday() not in day_list: #일 없는날 분기1
                return JsonResponse({'message' : f'not work on {full_date.strftime("%Y-%m-%d")}'}, status = 400)

            reservations  = Reservation.objects.filter(Q(doctor_id = doctor_id, date = full_date, status_id = 1) #취소된 예약의 시간은 불러오지않게
                                                     | Q(doctor_id = doctor_id, date = full_date, status_id = 2))                
            working_times = DoctorTime.objects.filter(days = full_date.weekday())
            time_list     = [time.time.strftime("%H:%M") for time in working_times]
            expired_time  = [reservation.time.strftime("%H:%M") for reservation in reservations]

            if len(time_list) == 0: #일 없는날 분기2
                return JsonResponse({'message' : f'not work on {full_date.strftime("%Y-%m-%d")}'}, status = 400)

            return JsonResponse({'working_times' : time_list,
                                 'expired_times' : expired_time}, status = 200)

        return JsonResponse({'result' : list(set(day_list))}, status = 200)
         
class ReservationView(View):
    @signin_decorator
    def get(self, request):
        try : 
            reservation_id = request.GET.get('res_id')
            reservation    = Reservation.objects.get(id = reservation_id)

            if reservation.user_id != request.user.id: #다른 환자의 진료 열람 X
                return JsonResponse({'message' : 'not allowed'}, status = 403)
            
            images = ReservationImage.objects.filter(reservation_id = reservation.id)\
                    .annotate(
                    url = Concat(Value(IP_ADDRESS), 'image', output_field = CharField()),
                    )

            image_list = [{
                'url' : image.url,
                'id'  : image.id
            } for image in images]

            result = {
                'status' :  reservation.status.name,
                'image' : image_list,
                'symptom' : reservation.symtom,
                'doctorOpinion' : reservation.opinion,
                'reservationDate' : convertor(reservation.date, reservation.time)
                }
            return JsonResponse({'result' : result}, status = 200)

        except Reservation.DoesNotExist:
            return JsonResponse({'message' : 'reservation not exists'}, status = 400)
    
    @signin_decorator
    def patch(self, request):
        try: 
            reservation_id = request.GET.get('res_id')
            work           = request.GET.get('work')
            user_id        = request.user.id
            reservation    = Reservation.objects.get(id = reservation_id)

            if reservation.user_id != user_id:
                return JsonResponse({'message' : 'not allowed'}, status = 403)

            if work == 'cancel':
                if reservation.status.name == '진료완료' or reservation.status.name == '진료취소': #진료완료거나 취소된거 취소못하게
                    return JsonResponse({'message' : 'already ended or canceled'}, status = 400)

                status_id = Status.objects.get(name='진료취소').id
                with transaction.atomic():
                    Reservation.objects.filter(id = reservation_id).update(status_id = status_id)
                    return JsonResponse({'message' : 'canceled'}, status = 201)
        
        except Reservation.DoesNotExist:
            return JsonResponse({'message' : 'reservation not exists'}, status = 400)

    @patient_decorator
    def post(self, request):
        try : 
            timedate    = datetime.now()
            user_id     = request.user.id
            doctor_id   = request.POST['doctor_id']
            symptom     = request.POST['symptom']
            year        = int(request.POST['year'])
            month       = int(request.POST['month'])
            day         = int(request.POST['date'])
            times       = request.POST['time']
            images      = request.FILES.getlist('img')
            format_time = time(int(times[:2]), int(times[3:]))
            format_date = datetime(year,month,day)
            
            if len(images) > 6:#이미지 6개 초과 방지
                return JsonResponse({'message' : 'images upload limit is 6'}, status = 400)

            if timedate.date() > format_date.date(): #과거날짜/시간으로 예약 방지
                return JsonResponse({'message' : 'not allowed to make reservation to old date'}, status = 400)

            if not DoctorDay.objects.filter(date = format_date).exists(): #일 안하는 날에 예약 생성 방지
                return JsonResponse({'message' : 'not working day'}, status = 400)
            
            working_times = DoctorTime.objects.filter(days = format_date.weekday())
            time_list     = [time.time.strftime("%H:%M") for time in working_times]
            if times not in time_list: #일 안하는 시간에 예약 생성 방지
                return JsonResponse({'message' : 'not working time'}, status = 400)

            if Reservation.objects.filter(Q(doctor_id = doctor_id, date = format_date, time = format_time, status_id = 1) 
                                        | Q(doctor_id = doctor_id, date = format_date, time = format_time, status_id = 2)).exists():#취소된 예약 제외 중복시간 방지
                return JsonResponse({'message' : 'that time already reserved'}, status = 400)

            with transaction.atomic():
                status = Status.objects.get(name="진료대기")
                Reservation.objects.create(
                    user_id = user_id,
                    doctor_id = doctor_id,
                    symtom = symptom,
                    date = format_date.strftime("%Y-%m-%d"),
                    time = times,
                    status_id = status.id
                )
            with transaction.atomic():
                reservation = Reservation.objects.get(user_id = user_id, doctor_id = doctor_id, symtom = symptom, 
                                                      time = format_time,status_id = status.id, date = format_date)
                imgs = [
                    ReservationImage(
                        image          = image,
                        reservation_id = reservation.id
                    )
                    for image in images
                ]
                ReservationImage.objects.bulk_create(imgs)
            return JsonResponse({'message' : 'reservation created'}, status = 201)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)

class ReservationsView(View):
    @signin_decorator
    def get(self, request):
        page   = int(request.GET.get('page', 1))
        limit  = int(request.GET.get('limit', 5))
        reservations = Reservation.objects.filter(user_id = request.user.id)\
                        .select_related('doctor', 'status', 'user')\
                        .annotate(
                            doctor_image   = Concat(Value(IP_ADDRESS), 'doctor__profile_image', output_field = CharField()),
                            doctor_name    = Concat('doctor__user__name', Value(''), output_field = CharField()),
                            hospital_name  = Concat('doctor__hospital__name', Value(''), output_field = CharField()),
                            subject_name   = Concat('doctor__subject__name', Value(''), output_field = CharField()),
                            status_name    = Concat('status__name', Value('') ,output_field = CharField()),
                            reservation_id = Concat('id', Value(''), output_field = CharField()),)\
                        .values('status_name','doctor_image', 'doctor_name', 'hospital_name', 'subject_name', 'reservation_id','date','time')\
                        .order_by('date', 'time')
        reservations = Paginator(reservations, limit)
        return JsonResponse({'result' : list(reservations.page(page).object_list)}, status = 200)

            

