from django.urls import path
from users.views import SignupView, SigninView,\
                        EmailUniqueCheckView, PasswordValidationView, Check

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/email_check', EmailUniqueCheckView.as_view()),
    path('/password_check', PasswordValidationView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/check', Check.as_view()),
]