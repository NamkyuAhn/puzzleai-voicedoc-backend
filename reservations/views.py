from users.models      import Subject, Doctor
from core.functions    import signin_decorator
from voicedoc.settings import IP_ADDRESS

from django.views import View
from django.http  import JsonResponse
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
        return JsonResponse({"result" : list(subjects)}, status = 200)

class DoctorView(View):
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