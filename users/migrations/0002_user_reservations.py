# Generated by Django 4.0.4 on 2022-06-14 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reservations',
            field=models.ManyToManyField(related_name='user_reservation', through='reservations.Reservation', to='users.doctor'),
        ),
    ]
