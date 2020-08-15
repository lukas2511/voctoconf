# Generated by Django 2.2.15 on 2020-08-14 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('text_de', models.TextField(blank=True, null=True)),
                ('text_en', models.TextField(blank=True, null=True)),
            ],
        ),
    ]