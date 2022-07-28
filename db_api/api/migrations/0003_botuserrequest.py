# Generated by Django 4.0.6 on 2022-07-27 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_botuser_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotUserRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bot_user_id', models.IntegerField()),
                ('date', models.DateField(auto_now=True)),
                ('time', models.TimeField(auto_now=True)),
                ('requested_url', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
