# 주식 종목 조회
from project import views
from core.constants import *
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client
import pythoncom
from project.actions.UserConnectionManager import XAConnector
import time


class XAStockSearchEvent:
    def stock_search(request):
        time.sleep(0.5)
        # 서버로 부터 종목 유형(코스피, 코스닥 or 전체), 종목 이름 받기
        stock_category = request.POST.get("stockCategory").strip()
        stock_name = request.POST.get("stockName").strip()
        print("외부에서 들어온 데이터 목록\n  =>stock_category : ", stock_category, "\n  =>stock_name : ", stock_name)
        

        # 데이터 검증
        if (stock_category == "" or stock_name == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '해당 종목은 존재하지 않습니다.', 'errorCode' : VALUEERROR}))
            
        is_continue = False
        response_data = XAConnector.stock_search(XAConnector, stock_category, is_continue)
        is_continue = True
        # dll파일을 통해 데이터 받기
        # stock_lists = XAConnector.stock_search(XAConnector, stock_category)

        # 받은 데이터 가공하기
        if (response_data == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'ConnectionRefusedError', 'errorCode' : SESSIONOUT}))
        elif (response_data == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'TimeoutError', 'errorCode' : SESSIONOUT}))
    
        # 유저가 원하는 데이터만 따로 세팅
        data = []
        print("response_data???? : ", response_data)
        for stock_list in response_data:
            if stock_name in stock_list['hname']:
                data.append(stock_list)
            else:
                continue
    
        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))
