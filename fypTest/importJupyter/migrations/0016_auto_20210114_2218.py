# Generated by Django 3.0.3 on 2021-01-14 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0015_auto_20210114_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebookmodel',
            name='notebook_html',
            field=models.TextField(default='dwdw'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notebookmodel',
            name='notebook_test_html',
            field=models.TextField(default='grrrr'),
            preserve_default=False,
        ),
    ]
