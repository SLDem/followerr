# Generated by Django 3.1.3 on 2020-11-19 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photoalbums', '0010_auto_20201112_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
