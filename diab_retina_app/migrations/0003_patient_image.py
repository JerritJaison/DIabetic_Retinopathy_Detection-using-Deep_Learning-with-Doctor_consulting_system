# Generated by Django 5.0.4 on 2024-04-20 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diab_retina_app', '0002_doctor'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
