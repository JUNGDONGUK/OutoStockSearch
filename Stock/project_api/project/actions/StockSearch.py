# 주식 종목 조회
from project import views
from django.http import HttpResponseRedirect,HttpResponse
from core import constants
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client
import pythoncom
from project.actions.UserConnectionManager import XAConnector


class XAStockSearchEvent:
    def stockSearch(request):
        # 서버로 부터 종목 유형(코스피, 코스닥 or 전체), 종목 이름 받기
        stockCategory = request.GET.get("stockCategory").strip()
        stockName = request.GET.get("stockName").strip()
        print("stockCategory : ", stockCategory, "\nstockName : ", stockName)
        

        # 데이터 검증
        if (stockCategory == "" or stockName == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '해당 종목은 존재하지 않습니다.'}))
        
        # dll파일을 통해 데이터 받기
        print('데이터 받기 시작')
        stockList = XAConnector.stockSearch(XAConnector, stockCategory)
        print('데이터 받아오기 성공')

        # 유저가 원하는 데이터만 따로 세팅
        data = []
        for i in stockList:
            if stockName in i['hname']:
                data.append(i)
            else:
                continue

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))
