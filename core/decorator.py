from django.http  import JsonResponse
from users.models import User

def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            user_id = request.session['user_id']
            request.user = User.objects.get(id=user_id)
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message':'IVALID_USER'},status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

def patient_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            user_id = request.session['user_id']
            user = User.objects.get(id=user_id)
            if request.user.is_doctor == True : 
                return False
            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message':'IVALID_USER'},status=401)
        except KeyError:
            return JsonResponse({'message' : 'signin time expired'})
    return wrapper

