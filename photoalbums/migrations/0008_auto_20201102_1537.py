# Generated by Django 3.1.1 on 2020-11-02 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photoalbums', '0007_remove_image_avatar_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(blank=True, max_length=4000, null=True, verbose_name='Description'),
        ),
    ]