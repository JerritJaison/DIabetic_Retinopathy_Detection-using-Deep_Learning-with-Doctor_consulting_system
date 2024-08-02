# Generated by Django 5.0.4 on 2024-04-20 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diab_retina_app', '0003_patient_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=100)),
                ('time', models.CharField(max_length=100)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='diab_retina_app.doctor')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='diab_retina_app.patient')),
            ],
        ),
    ]
