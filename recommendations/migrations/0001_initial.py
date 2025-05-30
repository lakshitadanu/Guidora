# Generated by Django 4.2.7 on 2025-04-22 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CareerPath',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('required_skills', models.TextField()),
                ('average_salary', models.CharField(max_length=100)),
                ('growth_prospects', models.TextField()),
                ('education_requirements', models.TextField()),
                ('stream_suitability', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=100)),
                ('website', models.URLField()),
                ('description', models.TextField()),
                ('courses_offered', models.TextField()),
                ('admission_process', models.TextField()),
                ('ranking', models.IntegerField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='institutes/')),
            ],
        ),
        migrations.CreateModel(
            name='UserRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('confidence_scores', models.JSONField()),
                ('career_path1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_recommendation', to='recommendations.careerpath')),
                ('career_path2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_recommendation', to='recommendations.careerpath')),
                ('career_path3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='third_recommendation', to='recommendations.careerpath')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
