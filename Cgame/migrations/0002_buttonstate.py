# Generated by Django 4.2.16 on 2024-12-11 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cgame', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('clicked', 'Clicked'), ('unclicked', 'Unclicked')], default='unclicked', max_length=10)),
                ('last_clicked', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='button_state', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]