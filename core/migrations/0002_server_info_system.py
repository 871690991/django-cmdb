# Generated by Django 4.1 on 2022-09-02 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='server_info',
            name='system',
            field=models.CharField(max_length=30, null=True, verbose_name='操作系统'),
        ),
    ]
