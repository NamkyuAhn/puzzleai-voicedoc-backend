import json

from users.models     import User
from users.validation import Validation

from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.db.utils        import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth    import authenticate, logout

class SignupView(View):
    def post(self, request):
        try:
            data      = json.loads(request.body)
            name      = data['name']
            email     = data['email']
            is_doctor = data['is_doctor']
            password  = data['password']

            Validation.email_validate(email)
            Validation.password_validate(password)

            User.objects.create_user(
                name      = name,
                password  = password,
                email     = email,
                is_doctor = is_doctor
            )
            return JsonResponse({'message' : 'signup success'}, status = 201)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)

        except IntegrityError:
            return JsonResponse({'message' : 'email is already exists'}, status = 400)

        except ValueError as e:
            return JsonResponse({'message' : f'{e}'}, status = 400)

        except ValidationError as e:
            e = str(e)[2:-2]
            return JsonResponse({'message' : f'{e}'}, status = 400)

class EmailValidationView(View):
    def post(self, request):
        try:
            data      = json.loads(request.body)
            email     = data['email']
            Validation.email_validate(email)
            return JsonResponse({'message' : 'email validation pass'}, status = 200)

        except ValidationError as e:
            e = str(e)[2:-2]
            return JsonResponse({'message' : f'{e}'}, status = 400)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)

class PasswordValidationView(View):
    def post(self, request):
        try:
            data      = json.loads(request.body)
            password  = data['password']
            Validation.password_validate(password)
            return JsonResponse({'message' : 'password validation pass'}, status = 200)
            
        except ValidationError as e:
            e = str(e)[2:-2]
            return JsonResponse({'message' : f'{e}'}, status = 400)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)

class SigninView(View):
    def post(self, request):
        data     = json.loads(request.body)
        email    = data['email']
        password = data['password']

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_doctor == True:
                #의사가 환자앱에서 로그인하면 거부/무조건 거부 x
                return JsonResponse({'message' : 'please signin on app for doctor'}, status = 400)

            request.session['user_id'] = user.id
            print(request.META['HTTP_USER_AGENT'])
            return JsonResponse({'message' : 'signin success', 'user_agent' : request.META['HTTP_USER_AGENT']}, status = 200)
        else:
            return JsonResponse({'message' : 'check email or password'}, status = 400)

class Logout(View):
    def post(self, request):
        logout(request)
        return HttpResponse("You're logged out.")
