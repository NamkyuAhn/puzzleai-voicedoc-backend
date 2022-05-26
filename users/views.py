import json

from users.models     import User
from users.validation import Validation

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import IntegrityError
from django.core.exceptions import ValidationError

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
