# Generated by Django 2.2.15 on 2020-08-14 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0005_auto_20200814_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='hide',
            field=models.BooleanField(default=False),
        ),
    ]
