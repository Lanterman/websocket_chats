from django.urls import path

from main import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('chat/<slug:chat_slug>/', views.chat_detail, name="chat_detail"),
]
