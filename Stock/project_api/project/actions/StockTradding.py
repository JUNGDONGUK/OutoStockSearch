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

class XAStockTraddingEvent:
    def stock_tradding(request):
        time.sleep(0.5)
        # 클라이언트 단에서 값 가져오기
        acnt_no = request.POST.get("AcntNo")
        input_pw = request.POST.get("InptPwd")
        isu_no = request.POST.get("IsuNo")
        ord_qty = request.POST.get("OrdQty")
        prd_prc = request.POST.get("OrdPrc")
        bns_tp_code = request.POST.get("BnsTpCode")
        ordprc_ptn_code = request.POST.get("OrdprcPtnCode")
        
        # 데이터 검증
        if (acnt_no == "" or acnt_no == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'stock_tradding에서 차트를 불러오는 도중  발생하였습니다.', 'errorCode' : VALUEERROR}))
        
        # dll파일을 통해 데이터 받기
        data = XAConnector.stock_tradding(XAConnector, acnt_no, input_pw, isu_no, ord_qty, prd_prc, bns_tp_code, ordprc_ptn_code)
        if (data == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        elif (data == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))

        print('매매는 성공')

        # 거래 내역 조회하기
        account_is_continue = False
        transaction_details = XAConnector.user_data_search(XAConnector, acnt_no, input_pw, account_is_continue)
        if (transaction_details == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        elif (transaction_details == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        print('거래내역조회 성공')

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data, 'userProperty' : transaction_details[0], 'transactionDetails': transaction_details[1]}))
