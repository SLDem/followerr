# Generated by Django 3.1.3 on 2020-11-04 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photoalbums', '0008_auto_20201102_1537'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='picture',
            new_name='image',
        ),
    ]
