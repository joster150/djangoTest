# Generated by Django 3.0.3 on 2020-12-23 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0003_step_tracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='step_tracker',
            name='name',
            field=models.CharField(default='track', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]