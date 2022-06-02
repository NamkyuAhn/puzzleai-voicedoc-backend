from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, name, email, is_doctor, password):
        if not name:            
            raise ValueError('must have user name')
        if not email:            
            raise ValueError('must have user email')
        if not is_doctor:            
            raise ValueError('must have user is_doctor')
        if not password:            
            raise ValueError('must have user password')

        user = self.model(            
            email     = self.normalize_email(email),         
            name      = name,
            is_doctor = is_doctor
        )

        user.set_password(password)        
        user.save(using=self._db)        
        return user

class User(AbstractBaseUser):
    name         = models.CharField(max_length=100)
    email        = models.EmailField(verbose_name='email', max_length=255, unique=True)
    is_doctor    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    reservations = models.ManyToManyField('users.Doctor', through='reservations.Reservation', related_name='user_reservation')
    USERNAME_FIELD = 'email'
    objects = UserManager()

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
    name  = models.CharField(max_length=30)
    image = models.FileField(upload_to="subject_images", null=True)

    class Meta:
        db_table = 'subjects'
