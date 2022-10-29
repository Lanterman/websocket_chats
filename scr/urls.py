from django.urls import path, include

urlpatterns = [
    path('', include('scr.main.urls'), name="main"),
]
