# Generated by Django 2.2.9 on 2022-11-16 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20221115_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='а URLField можно?', unique=True, verbose_name='уникальный адрес'),
        ),
    ]
