from django.urls import path
from users.views import SignupView, SigninView, EmailUniqueCheckView, UserIdCheck

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/email_check', EmailUniqueCheckView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/check', UserIdCheck.as_view()),
]