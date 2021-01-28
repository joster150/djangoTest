# Generated by Django 3.0.3 on 2021-01-12 14:55

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0009_auto_20210112_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebookmodel',
            name='name',
            field=models.CharField(default='aname', max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notebookmodel',
            name='functions',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
