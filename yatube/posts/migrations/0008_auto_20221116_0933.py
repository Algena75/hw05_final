# Generated by Django 2.2.9 on 2022-11-16 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20221116_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='group_posts', to='posts.Group', verbose_name='соответствующая группа'),
        ),
    ]