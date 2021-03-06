# Generated by Django 3.0.3 on 2020-12-26 22:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('importJupyter', '0005_remove_step_tracker_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pipelines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_num', models.IntegerField(default=1)),
                ('module', models.CharField(max_length=120)),
                ('function', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('output', models.CharField(max_length=120)),
                ('pipeline_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='importJupyter.Pipelines')),
            ],
            options={
                'unique_together': {('pipeline_id', 'step_num')},
            },
        ),
    ]
