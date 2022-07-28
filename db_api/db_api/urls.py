from api.views import BotUserDetail, BotUserRequestDetail, MessageDetail
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('api/message/<pk>', MessageDetail.as_view()),
    path('api/request/', BotUserRequestDetail.as_view()),
    path('api/user/', BotUserDetail.as_view()),
    path('admin/', admin.site.urls),
]
