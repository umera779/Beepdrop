# Generated by Django 4.2.16 on 2025-01-03 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cgame', '0004_delete_invite'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='telegram_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
