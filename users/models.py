from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    username     = models.CharField(max_length=100)
    email        = models.EmailField(verbose_name='email', max_length=255, unique=True)
    is_doctor    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    reservations = models.ManyToManyField('users.Doctor', through='reservations.Reservation', related_name='user_reservation')

    class Meta:
        db_table = 'users'

class Doctor(models.Model):
    user          = models.OneToOneField('users.User', on_delete=models.CASCADE)
    hospital      = models.ForeignKey('users.Hospital', on_delete=models.SET_NULL, null = True)
    subject       = models.ForeignKey('users.Subject', on_delete=models.SET_NULL, null = True)
    profile_image = models.FileField(upload_to="doctor_profile_images")
    working_days  = models.CharField(max_length=100)
    working_times = models.CharField(max_length=500)
    
    class Meta:
        db_table = 'doctors'

class Hospital(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = 'hospitals'

class Subject(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = 'subjects'

