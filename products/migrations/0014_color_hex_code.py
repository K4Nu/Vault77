# Generated by Django 5.1.7 on 2025-04-13 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_remove_category_gender_alter_category_size_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='color',
            name='hex_code',
            field=models.CharField(default='FFFFFF', max_length=6),
        ),
    ]
