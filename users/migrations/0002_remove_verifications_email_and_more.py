# Generated by Django 4.2.1 on 2023-12-04 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verifications',
            name='email',
        ),
        migrations.AddField(
            model_name='verifications',
            name='phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
