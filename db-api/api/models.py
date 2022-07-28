from django.db import models


class Message(models.Model):
    name = models.CharField(primary_key=True, max_length=20)
    text = models.CharField(max_length=200)


class BotUser(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(null=True, max_length=50)
    last_name = models.CharField(null=True, max_length=50)
    username = models.CharField(null=True, max_length=50)
    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10)


class BotUserRequest(models.Model):
    bot_user_id = models.IntegerField(null=True,)
    date = models.DateField(null=True, auto_now=True)
    time = models.TimeField(null=True, auto_now=True)
    requested_url = models.CharField(null=True, max_length=50)
