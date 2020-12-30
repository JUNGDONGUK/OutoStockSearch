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
class LoginManager(XAConnector):

    def do_login(request):
        # try:
        # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
        if super().xa_session() != None:
            print('연결 되어 있습니다.')
        else :
            print('연결 되어 있지 않습니다. 연결을 시도합니다.')
            super().connect_server()
        if request.method == 'POST':
            user_id = request.POST.get("userId")
            user_pw = request.POST.get("userPw")
            cert_pw = request.POST.get("userCertPassword")
        super().login(user_id, user_pw, cert_pw)
        
        data = {
            'user_id' : user_id,
            'accounts' : super().get_account_list()
        }
        # HttpResponse.set_cookie('accessCookie', data)
        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))

        # except :
        #     return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '유저 정보를 가져오는 도중  발생하였습니다.'}))

    def do_logout(request):
        if super().disconnect_server():
            return HttpResponse(json.dumps({'status' : 'SUCCESS'}))
        else:
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '발생하였습니다.'}))
        




