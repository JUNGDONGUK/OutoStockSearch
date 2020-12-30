# 주식 종목 조회
from project import views
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client
import pythoncom
from project.actions.UserConnectionManager import XAConnector
from core.constants import *
from datetime import datetime
import time

class XAStockChartEvent:
    def stock_chart(request):
        time.sleep(0.5)
        # 클라이언트 단에서 값 가져오기
        shcode = request.POST.get("shcode")
        gubun = request.POST.get("gubun")
        ncnt = request.POST.get("ncnt")
        qrycnt = request.POST.get("qrycnt")
        sdate = request.POST.get("sdate")
        edate = request.POST.get("edate")
        acnt_no = request.POST.get("AcntNo")
        input_pw = request.POST.get("AccountPw")

        # 데이터 검증
        if (shcode == "" or shcode == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'stock_chart에서 차트를 불러오는 도중  발생하였습니다.', 'errorCode' : VALUEERROR}))
        
        # 데이터 연속조회 여부 판단
        chart_is_continue = False
        account_is_continue = False

        # dll파일을 통해 데이터 받기
        data = XAConnector.stock_chart(XAConnector, shcode, gubun, ncnt, qrycnt, sdate, edate, chart_is_continue)
        if (data == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        elif (data == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))

        
        # 거래 내역 조회하기
        datas = XAConnector.user_data_search(XAConnector, acnt_no, input_pw, account_is_continue)
        if (datas == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        elif (datas == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        print('거래내역조회 성공')

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data, 'userProperty' : datas[0], 'transactionDetails': datas[1]}))
