from datetime import datetime, date, time

from reservations.models import Reservation
from users.models        import Subject, Doctor, DoctorDay, DoctorTime
from core.functions      import signin_decorator
from voicedoc.settings   import IP_ADDRESS

from django.views import View
from django.http  import JsonResponse
from django.db.models.functions import Concat
from django.db.models           import CharField, Value

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
            file_location = Concat(
                Value(IP_ADDRESS), 'profile_image', output_field = CharField()),
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

        if dates != None: 
            full_date = datetime(int(year), int(month), int(dates))
            current   = datetime.now()
            if current.day > full_date.day: #과거시간 조회 못하게
                return JsonResponse({'message' : "you can't read old calaneder"}, status = 400)

            reservations  = Reservation.objects.filter(doctor_id = doctor_id, date = full_date)
            working_times = DoctorTime.objects.filter(days = full_date.weekday())
            time_list     = [str(time.times) for time in working_times]
            expired_time  = [reservation.time.strftime("%H:%M") for reservation in reservations]

            if len(time_list) == 0: #일 없는날 분기
                return JsonResponse({'message' : f'not work on {full_date.strftime("%Y-%m-%d")}'}, status = 400)

            return JsonResponse({'working_times' : time_list,
                                 'expired_times' : expired_time}, status = 200)

        days     = DoctorDay.objects.filter(doctor_id = doctor_id)
        day_list = [day.date.weekday() for day in days 
                    if day.date.month == month and day.date.year == year]
        return JsonResponse({'result' : list(set(day_list))}, status = 200)
                    

            

