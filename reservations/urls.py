from django.urls import path
from reservations.views import SubjectView, DoctorListView, DoctorWorkView,\
                               ReservationView

urlpatterns = [
    path('/subject', SubjectView.as_view()),
    path('/subject/<int:subject_id>', DoctorListView.as_view()),
    path('/time/<int:doctor_id>', DoctorWorkView.as_view()),
    path('', ReservationView.as_view()),
]