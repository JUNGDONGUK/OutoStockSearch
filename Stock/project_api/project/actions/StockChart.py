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


class XAStockChartEvent:
    def stockChart(request):
        # 클라이언트 단에서 값 가져오기
        shcode = request.POST.get("shcode")
        gubun = request.POST.get("gubun")
        ncnt = request.POST.get("ncnt")
        qrycnt = request.POST.get("qrycnt")
        sdate = request.POST.get("sdate")
        edate = request.POST.get("edate")

        # 데이터 검증
        if (shcode == "" or shcode == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '차트를 불러오는 도중 오류가 발생하였습니다.'}))
        
        # dll파일을 통해 데이터 받기
        stockList = XAConnector.stockChart(XAConnector, shcode, gubun, ncnt, qrycnt, sdate, edate)

        # 유저가 원하는 데이터만 따로 세팅
        data = []
        for i in stockList:
            if stockName in i['hname']:
                data.append(i)
            else:
                continue

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))
