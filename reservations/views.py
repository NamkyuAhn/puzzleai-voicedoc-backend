from datetime import datetime

from reservations.models import Reservation, ReservationImage, Status
from users.models        import Subject, Doctor, DoctorDay, DoctorTime
from core.functions      import signin_decorator, convertor
from voicedoc.settings   import IP_ADDRESS

from django.views import View
from django.http  import JsonResponse
from django.db    import transaction
from django.db.models.functions import Concat
from django.db.models           import CharField, Value, Q

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
        doctors = Doctor.objects.filter(subject_id = subject_id)\
        .select_related('subject', 'hospital', 'user')\
        .annotate(
            file_location = Concat(Value(IP_ADDRESS), 'profile_image', output_field = CharField()),
            name          = Concat('user__name', Value(''),output_field = CharField()),
            hospital_name = Concat('hospital__name', Value(''),output_field = CharField()),
            subject_name  = Concat('subject__name', Value(''),output_field = CharField()),
            )\
        .values('id', 'name', 'file_location', 'hospital_name', 'subject_name')
        return JsonResponse({'result' : list(doctors)}, status = 200)

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

            #reservations  = Reservation.objects.filter(doctor_id = doctor_id, date = full_date)
            reservations  = Reservation.objects.filter(Q(doctor_id = doctor_id, date = full_date, status_id = 1) | Q(doctor_id = doctor_id, date = full_date, status_id = 2))                
            working_times = DoctorTime.objects.filter(days = full_date.weekday())
            time_list     = [str(time.times) for time in working_times]
            expired_time  = [reservation.time.strftime("%H:%M") for reservation in reservations]

            if len(time_list) == 0: #일 없는날 분기2
                return JsonResponse({'message' : f'not work on {full_date.strftime("%Y-%m-%d")}'}, status = 400)

            return JsonResponse({'working_times' : time_list,
                                 'expired_times' : expired_time}, status = 200)

        return JsonResponse({'result' : list(set(day_list))}, status = 200)
         
class ReservationView(View):
    @signin_decorator
    def get(self, request, reservation_id):
        try : 
            reservation = Reservation.objects.get(id = reservation_id)

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
    def patch(self, request, reservation_id):
        try: 
            work        = request.GET.get('work')
            user_id     = request.user.id
            reservation = Reservation.objects.get(id = reservation_id)

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
   

        

            

