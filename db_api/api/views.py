from rest_framework import generics

from .models import BotUser, BotUserRequest, Message
from .serializers import (BotUserRequestSerializer, BotUserSerializer,
                          MessageSerializer)


class MessageDetail(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class BotUserDetail(generics.CreateAPIView):
    queryset = BotUser.objects.all()
    serializer_class = BotUserSerializer


class BotUserRequestDetail(generics.CreateAPIView):
    queryset = BotUserRequest.objects.all()
    serializer_class = BotUserRequestSerializer
