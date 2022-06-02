from django.urls import path
from reservations.views import SubjectView, DoctorView

urlpatterns = [
    path('/subject', SubjectView.as_view()),
    path('/subject/<int:subject_id>', DoctorView.as_view())
]