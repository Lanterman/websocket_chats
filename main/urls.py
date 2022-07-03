from django.urls import path

from main import views

urlpatterns = [
    path('', views.ListMainPageView.as_view(), name="main_page"),
    path('chat/<slug:chat_slug>/', views.ChatDetailView.as_view(), name="chat_detail"),
]
