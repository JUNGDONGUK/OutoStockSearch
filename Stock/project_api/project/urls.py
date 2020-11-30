from django.urls import path, re_path
from project import views
from django.conf.urls import url
from project.actions import UserAccountSearch, UserLogin

urlpatterns = [
    path("", views.main, name='main'),
    path("login/", UserLogin.doLogin, name='login'),
    path("account/", UserAccountSearch.XAUserDataSelectEvent.accountSelect, name='login'),
]
