from django.urls import path, re_path
from project import views
from django.conf.urls import url
from project.actions import UserAccountSearch, UserLogin, StockSearch, StockChart, StockTradding, StockSystemTradding

urlpatterns = [
    path("", views.main, name='main'),
    path("login/", UserLogin.LoginManager.do_login, name='login'),
    path("logout/", UserLogin.LoginManager.do_logout, name='logout'),
    path("account/", UserAccountSearch.XAUserDataSelectEvent.account_select, name='accountSearch'),
    path("stockDetail/", StockChart.XAStockChartEvent.stock_chart, name='stockChart'),
    # re_path(r'stocksearch/$', StockSearch.XAStockSearchEvent.stock_search, name='stocksearch'),
    path("stocksearch/", StockSearch.XAStockSearchEvent.stock_search, name='stocksearch'),
    path("tradding/", StockTradding.XAStockTraddingEvent.stock_tradding, name='stockTradding'),
    path("systemTradding/", StockSystemTradding.XAStockSystemTraddingEvent.stock_system_tradding, name='systemTradding'),
]
