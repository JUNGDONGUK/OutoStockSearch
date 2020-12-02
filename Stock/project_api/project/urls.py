from django.urls import path, re_path
from project import views
from django.conf.urls import url
from project.actions import UserAccountSearch, UserLogin, StockSearch, StockChart

urlpatterns = [
    path("", views.main, name='main'),
    path("login/", UserLogin.LoginManager.doLogin, name='login'),
    path("account/", UserAccountSearch.XAUserDataSelectEvent.accountSelect, name='accountSearch'),
    path("stockDetail/", StockChart.XAStockChartEvent.stockChart, name='stockChart'),
    re_path(r'stocksearch/$', StockSearch.XAStockSearchEvent.stockSearch, name='stocksearch'),
]
