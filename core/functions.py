import jwt

from datetime import datetime, timedelta

from django.http  import JsonResponse

from users.models      import User
from voicedoc.settings import SECRET, ALGORITHM

def jwt_generator(user_id):
    payload = {'user_id' : user_id, 'exp' : datetime.utcnow()+ timedelta(hours=1)}
    encoded = jwt.encode(payload, SECRET, algorithm = ALGORITHM)
    return encoded

def jwt_decoder(token):
    try: 
        decoded = jwt.decode(token, SECRET, algorithms = ALGORITHM)
        return decoded
    except jwt.exceptions.ExpiredSignatureError:
        raise KeyError
    
def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization", None)
            request.user = User.objects.get(id=jwt_decoder(token)['user_id'])
            request.payload = jwt_decoder(token)
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'IVALID_USER'}, status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

def patient_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization", None)
            request.user = User.objects.get(id=jwt_decoder(token)['user_id'])
            if request.user.is_doctor == True : 
                return JsonResponse({'message': "doctor can't access to patient menu"}, status = 403)
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'IVALID_USER'}, status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

def convertor(day, time):
    date = '()'
    time_format = '오전'
    if day.weekday() == 0:
        date = '(월)'
    elif day.weekday() == 1:
        date = '(화)'
    elif day.weekday() == 2:
        date = '(수)'
    elif day.weekday() == 3:
        date = '(목)'
    elif day.weekday() == 4:
        date = '(금)'
    elif day.weekday() == 5:
        date = '(토)'
    elif day.weekday() == 6:
        date = '(일)'
    if time.hour >= 13 :
        time_format = '오후'
        
    return day.strftime("%Y-%m-%d") + date + ' ' + time_format + ' '+ time.strftime("%H:%M") 