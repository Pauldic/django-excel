# Generated by Django 3.2.6 on 2021-09-07 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskreport',
            options={'ordering': ['site', 'task'], 'verbose_name': 'Task Report', 'verbose_name_plural': 'Task Reports'},
        ),
    ]
