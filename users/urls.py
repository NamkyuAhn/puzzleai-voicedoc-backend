from django.urls import path
from users.views import SignupView, SigninView, Logout, \
                        EmailValidationView, PasswordValidationView

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/email_check', EmailValidationView.as_view()),
    path('/password_check', PasswordValidationView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/logout', Logout.as_view()),
]