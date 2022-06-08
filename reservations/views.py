from datetime import date

from reservations.models import Reservation
from users.models        import Subject, Doctor, DoctorDay, DoctorTime
from core.functions      import signin_decorator
from voicedoc.settings   import IP_ADDRESS

from django.views import View
from django.http  import JsonResponse, HttpResponse
from django.db.models.functions import Concat
from django.db.models           import CharField, Value

class SubjectView(View):
    @signin_decorator
    def get(self, request):
        subjects  = Subject.objects.annotate(
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
    def get(self, request, doctor_id):
        try:
            year   = request.GET.get('year')
            month  = request.GET.get('month')
            dates  = request.GET.get('dates', None)

            if dates != None: 
                full_day = f'{year}-{month}-{dates}'
                reservations = Reservation.objects.filter(doctor_id = doctor_id, date = full_day)
                day = date(int(year), int(month), int(dates)).weekday()
                working_time = DoctorTime.objects.get(days = day).times
                time_list = working_time.split(',')
                working_times = {'times' : time_list}
                expired_time = [reservation.time for reservation in reservations]
                return JsonResponse({'working_times' : working_times,
                                    'expired_times' : expired_time}, status = 200)

            working_day = DoctorDay.objects.get(doctor_id = doctor_id, 
                                    year = year, month = month).days
            time_lists = working_day.split(",")
            result = []
            for time in time_lists:
                result.append(int(time))
            return JsonResponse({'result' : result}, status = 200)

        except DoctorDay.DoesNotExist:
            return HttpResponse("조건에 부합하는 의사 근무날짜 없음")

        except DoctorTime.DoesNotExist:
            return HttpResponse("조건의 부합하는 의사 근무시간 없음")
              
                    

            

