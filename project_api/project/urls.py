from django.urls import path, re_path
from project import views, test
from django.conf.urls import url
from project.actions import UserAccountSearch, UserLogin, StockSearch, StockChart, StockTradding, StockSystemTradding, UserConnectionManager

urlpatterns = [
    path("", views.do_login, name='main'),
    path("login/", views.do_login, name='login'),
    path("logout/", views.do_logout, name='logout'),
    path("account/", views.account_select, name='accountSearch'),
    path("stockDetail/", views.stock_chart, name='stockChart'),
    # re_path(r'stocksearch/([-a-zA-Z0-9_]+)/([-a-zA-Z0-9_]+)/$', views.stock_item, name='stocksearch'),
    path("stocksearch/", views.stock_item, name='stocksearch'),
    path("tradding/", views.stock_tradding, name='stockTradding'),
    path("systemTradding/", views.stock_system_tradding, name='systemTradding'),
    path('webCrawling/', views.finance_crawling, name='webCrawling'),
    path('dataTunning/', views.tunning_data, name='dataTunning'),
    path('crawlingStockDetail/', views.crawlingStockDetail, name='crawlingStockDetail'),
]
