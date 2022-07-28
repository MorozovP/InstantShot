from rest_framework import serializers
from .models import Message, BotUser, BotUserRequest


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('text',)


class BotUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotUser
        fields = '__all__'


class BotUserRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotUserRequest
        fields = '__all__'