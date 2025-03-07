# Generated by Django 5.1.6 on 2025-03-05 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_url', models.URLField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
            ],
        ),
    ]
