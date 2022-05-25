import json

from users.models    import User
from django.views    import View
from django.http     import JsonResponse
from django.db.utils import IntegrityError

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