# Generated by Django 4.0.4 on 2022-06-02 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_user_groups_remove_user_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='image',
            field=models.FileField(null=True, upload_to='subject_images'),
        ),
    ]
