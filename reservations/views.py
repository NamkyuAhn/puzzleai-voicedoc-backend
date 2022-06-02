from users.models   import Subject, Doctor
from core.functions import signin_decorator

from django.views               import View
from django.http                import JsonResponse

class SubjectView(View):
    def get(self, request):
        subjects  = Subject.objects.all().prefetch_related("doctor_set")
        result = []

        for subject in subjects:
            file_location = '192.168.0.114:8000/media/' + str(subject.image)
            result.append({
                "subject_id" : subject.id,
                "subject_name" : subject.name,
                "subject_iamge" : file_location
            })
        return JsonResponse({"result" : result}, status = 200)

    def post(self, request):
        name  = request.POST['name']
        image = request.FILES.__getitem__('image')
        Subject.objects.create(name = name, image = image)
        return JsonResponse({'message' : 'success'}, status = 201)

class DoctorView(View):
    def get(self, request, subject_id):
        doctors = Doctor.objects.filter(subject_id = subject_id).select_related('subject', 'hospital', 'user')
        result = []

        for doctor in doctors:
            file_location = '192.168.0.114:8000/media/' + str(doctor.profile_image)
            result.append({
                "name" : doctor.user.name,
                "subject" : doctor.subject.name,
                "hospital" : doctor.hospital.name,
                "profile_image" : file_location
            })
        return JsonResponse({'result' : result}, status = 200)