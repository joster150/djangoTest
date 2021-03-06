# Generated by Django 3.0.3 on 2021-01-19 15:25

from django.db import migrations, models
import django.db.models.deletion
import importJupyter.models


class Migration(migrations.Migration):

    dependencies = [
        ('importJupyter', '0020_auto_20210118_1943'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentationImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=importJupyter.models.DocumentationImage.generate_image_path)),
                ('image_number', models.IntegerField(default=1)),
                ('caption', models.CharField(max_length=100)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='importJupyter.DocumentationPosts')),
            ],
            options={
                'unique_together': {('post', 'image_number')},
            },
        ),
    ]
