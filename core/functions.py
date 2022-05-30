import jwt
import datetime

from django.http  import JsonResponse

from users.models      import User
from voicedoc.settings import SECRET, ALGORITHM

def jwt_generator(payload, user_id):
    payload['user_id'] = user_id
    encoded = jwt.encode(payload, SECRET, algorithm = ALGORITHM)
    return encoded

def jwt_decoder(token):
    decoded = jwt.decode(token, SECRET, algorithms = ALGORITHM)
    return decoded

def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            user_id = request.session['user_id']
            request.user = User.objects.get(id=user_id)
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'IVALID_USER'},status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

def patient_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            user_id = request.session['user_id']
            request.user = User.objects.get(id=user_id)
            if request.user.is_doctor == True : 
                return JsonResponse({'message': "doctor can't access to patient menu"}, status = 403)
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'IVALID_USER'}, status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

