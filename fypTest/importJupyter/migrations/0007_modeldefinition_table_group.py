# Generated by Django 3.0.3 on 2021-01-09 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0006_pipeline_pipelines'),
    ]

    operations = [
        migrations.AddField(
            model_name='modeldefinition',
            name='table_group',
            field=models.CharField(default='Test', max_length=50),
        ),
    ]
