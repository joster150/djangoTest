# Generated by Django 3.0.3 on 2021-01-15 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0016_auto_20210114_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notebookmodel',
            name='name',
            field=models.SlugField(unique=True),
        ),
    ]