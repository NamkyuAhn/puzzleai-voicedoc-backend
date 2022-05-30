import json
import jwt 

from users.models    import User
from core.functions  import jwt_generator, jwt_decoder
 
from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.db.utils        import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth    import authenticate

class SignupView(View):
    def post(self, request):
        try:
            data      = json.loads(request.body)
            name      = data['name']
            email     = data['email']
            is_doctor = data['is_doctor']
            password  = data['password']

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

class EmailUniqueCheckView(View):
    def post(self, request):
        try:
            data      = json.loads(request.body)
            email     = data['email']
            if not User.objects.filter(email = email).exists():
                return JsonResponse({'message' : 'email unique check pass'}, status = 200)
            return JsonResponse({'message' : 'email already exists'}, status = 400)
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
        payload = {}

        if user is not None:
            if user.is_doctor == True: 
                app_checking = str(request.META['HTTP_USER_AGENT'])
                browser_list = ['Chrome', 'Safari', 'Edg']
                
                for browser in browser_list:
                    if browser in app_checking:
                        jwt_generator(payload, user.id)
                        return JsonResponse({'message' : 'signin success for doctor', 'token' : jwt_generator(payload, user.id)}, status = 200)
                    else: 
                        return JsonResponse({'message' : 'signin failed because you are not patient'}, status = 400)
            
            return JsonResponse({'message' : 'signin success', 'token' : jwt_generator(payload, user.id)}, status = 200)
            
        else:
            return JsonResponse({'message' : 'check email or password'}, status = 400)

class Check(View):
    def post(self, request):
        try:
            token = request.headers.get("Authorization", None)
            return JsonResponse({'your id' : jwt_decoder(token)}, status = 200)
        except KeyError:
            return HttpResponse('no token in request')
