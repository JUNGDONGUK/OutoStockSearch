# 5 유저 계좌 조회
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


# 계좌번호를 통한 데이터 조회
class XAUserDataSelectEvent:
    def accountSelect(request):
        # 서버로 부터 계좌번호, 비밀번호 받기
        responseData = {}
        accountNum = request.POST.get("accountNum").strip()
        accountPw = request.POST.get("accountPw").strip()
        if (accountNum == "" or accountNum == None) :
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '계좌정보가 존재하지 않습니다. 로그인페이지로 이동합니다.'}))

        responseData = XAConnector.userDataSearch(XAConnector, request, accountNum, accountPw)

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : responseData}))




