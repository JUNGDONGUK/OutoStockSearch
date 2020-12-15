import win32com.client
import pythoncom
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
from project.actions.UserConnectionManager import XAConnector


# 로그인 기능
class LoginManager:
    def do_login(request):
        try:
            print('접속상태 확인 : ', XAConnector.is_connected(XAConnector))
            if XAConnector.is_connected(XAConnector) == None :
                XAConnector.connect_server(XAConnector)

            # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
            if request.method == 'POST':
                user_id = request.POST.get("userId")
                user_pw = request.POST.get("userPw")
                cert_pw = request.POST.get("userCertPassword")
            XAConnector.login(XAConnector, user_id, user_pw, cert_pw)
            
            data = {
                'user_id' : user_id,
                'accounts' : XAConnector.get_account_list(XAConnector)
            }
            # HttpResponse.set_cookie('accessCookie', data)

            return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))
        except Exception as e:
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '유저 정보를 가져오는 도중  발생하였습니다.'}))

    def do_logout(request):
        if XAConnector.disconnect_server(XAConnector):
            return HttpResponse(json.dumps({'status' : 'SUCCESS'}))
        else:
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '발생하였습니다.'}))
        




