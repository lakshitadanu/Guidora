# Generated by Django 5.0.2 on 2025-04-23 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_user_areas_of_interest_remove_user_board_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collegestudent',
            name='areas_of_interest',
        ),
        migrations.RemoveField(
            model_name='schoolstudent',
            name='areas_of_interest',
        ),
        migrations.RemoveField(
            model_name='schoolstudent',
            name='entrance_exams',
        ),
    ]
