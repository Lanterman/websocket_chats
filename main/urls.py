from django.urls import path

from main import views

urlpatterns = [
    path('', views.ListMainPageView.as_view(), name="main_page"),
    path('chat/<slug:chat_slug>/', views.ChatDetailView.as_view(), name="chat_detail"),
    path('chat/<slug:chat_slug>/delete/', views.delete_chat, name="delete_chat"),
    path('chat/<slug:chat_slug>/leave/', views.leave_chat, name="leave_chat"),
    path('chat/<slug:chat_slug>/connect/', views.connect_to_chat, name="connect_to_chat"),
    path('user/<username>/', views.user_detail, name="user_detail"),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path("chat/<slug:chat_slug>/add_message/", views.add_message, name="add_message"),
    path("chat/<slug:chat_slug>/update_chat/", views.update_chat, name="update_chat"),
    path("chat/<slug:chat_slug>/is_read/", views.is_read, name="is_read"),
]
