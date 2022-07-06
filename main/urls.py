from django.urls import path

from main import views

urlpatterns = [
    path('', views.ListMainPageView.as_view(), name="main_page"),
    path('chat/<slug:chat_slug>/', views.ChatDetailView.as_view(), name="chat_detail"),
    path('chat/<slug:chat_slug>/delete/', views.delete_chat, name="delete_chat"),
    path('chat/<slug:chat_slug>/leave/', views.leave_chat, name="leave_chat"),
    path('user/<username>/', views.user_detail, name="user_detail")
]
