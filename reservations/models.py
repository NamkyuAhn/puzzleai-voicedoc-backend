from django.db import models

class Reservation(models.Model):
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE)
    doctor     = models.ForeignKey('users.Doctor', on_delete=models.CASCADE)
    status     = models.ForeignKey('reservations.Status', on_delete=models.CASCADE)
    symtom     = models.CharField(max_length=1000)
    opinion    = models.CharField(max_length=1000)
    date       = models.DateField(help_text="YYYY-MM-DD")
    time       = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservations'

class Status(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        db_table = 'statuses'

class ReservationImage(models.Model):
    reservation = models.ForeignKey('reservations.Reservation', on_delete=models.CASCADE)
    image       = models.FileField(upload_to="reservation_images")

    class Meta:
        db_table = 'reservation_images'