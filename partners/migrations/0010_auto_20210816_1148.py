# Generated by Django 2.2.24 on 2021-08-16 09:48

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0009_partner_is_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='logo',
            field=sorl.thumbnail.fields.ImageField(upload_to='partners'),
        ),
    ]
