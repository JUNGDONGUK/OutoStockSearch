# 5 유저 계좌 조회
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
import time


# 계좌번호를 통한 데이터 조회
class XAUserDataSelectEvent:
    def account_select(request):
        time.sleep(0.5)
        # 서버로 부터 계좌번호, 비밀번호 받기
        response_data = {}
        account_num = request.POST.get("accountNum").strip()
        account_pw = request.POST.get("accountPw").strip()
        if (account_num == "" or account_num == None) :
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '계좌정보가 존재하지 않습니다. 로그인페이지로 이동합니다.', 'errorCode' : VALUEERROR}))

        is_continue = False
        response_data = XAConnector.user_data_search(XAConnector, account_num, account_pw, is_continue)
        is_continue = True
        if (response_data == ConnectionRefusedError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))
        elif (response_data == TimeoutError):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '세션이 만료되었습니다.', 'errorCode' : SESSIONOUT}))

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'userProperty' : response_data[0], 'transactionDetails': response_data[1]}))




