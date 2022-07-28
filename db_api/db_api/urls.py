from django.contrib import admin
from django.urls import path

from api.views import MessageDetail, BotUserDetail, BotUserRequestDetail


urlpatterns = [
    path('api/message/<pk>', MessageDetail.as_view()),
    path('api/request/', BotUserRequestDetail.as_view()),
    path('api/user/', BotUserDetail.as_view()),
    path('admin/', admin.site.urls),
]
