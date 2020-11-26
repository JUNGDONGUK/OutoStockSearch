from django.urls import path, re_path
from project import views
from django.conf.urls import url

urlpatterns = [
    path("", views.main, name='main'),
    path("login/", views.doLogin, name='login'),
]
