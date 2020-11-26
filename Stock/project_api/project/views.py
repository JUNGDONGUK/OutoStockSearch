import win32com.client
import pythoncom
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from core import constants
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view


# 1. MainPage 접속
def main(reqeust): 
    # 여기서 reqeust는 무조건 들어오게 되어있다 왜? 요청에 대한 응답을 보내주는 부분이기 때문에 요청은 반드시 1개 이상 들어와야 정상이다.

    # 로그인 유무 판단 부분    
    if reqeust.session.get('user_id'):
        print("우음??")
        print("constants.MAINPAGE : ", constants.MAINPAGE)
        return HttpResponseRedirect(constants.MAINPAGE)
    else :
        return loginCheck(reqeust)


# 2. 로그인한 유저가 아닐 시 loginPage로 이동
def loginCheck(reqeust):
    return HttpResponseRedirect(constants.LOGINPAGE)


# 3. 로그인 이벤트 처리 클래스 구현
class XASessionEventHandler:

    def OnLogin(self, code, msg):
        if code == '0000':
            constants.LOGINSTATE = True
    def OnDisconnect(self, code, msg):
        pass


# 4. 로그인 기능
def doLogin(reqeust):
    # 4-1
    # COM을 사용하기 위해 라이브러리 초기화
    # 서브 스레드에서 COM 객체를 사용하려면 COM 라이브러리를 초기화 해야함
    pythoncom.CoInitialize()

    
    # 4-2
    # XASession 클래스에 대한 인스턴스를 생성 
    # DispatchWithEvents 함수의 첫 번째 인자로는 인스턴스를 생성하려는 클래스의 이름을 지정하면 됩니다. 
    # XASession 클래스는 XA_Session.dll이라는 파일에 구현돼 있으므로 'XA_Session.XASession'을 입력했습니다.
    instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)

    # 4-3
    # COM을 사용 후 라이브러리 초기화
    pythoncom.CoUninitialize()


    # 4-4
    # 화면에서 값 받아 접속할 ID PW, 를 지정하기
    
        # 4-4-1
        # 본 서버
    if reqeust.method == 'POST':
        constants.REAL_LOGINID = reqeust.POST.get("userId")
        constants.REAL_LOGINPASSWORD = reqeust.POST.get("userPw")
        constants.REAL_LOGINCERTPASSWORD = reqeust.POST.get("userCertPassword")
    user_id = constants.REAL_LOGINID
    user_pw = constants.REAL_LOGINPASSWORD
    cert_pw = constants.REAL_LOGINCERTPASSWORD 
    
        # 4-4-2
        # 모의거래 서버
    # if reqeust.method == 'POST':
    #     constants.DEMO_LOGINID = reqeust.POST.get("userId")
    #     constants.DEMO_LOGINPASSWORD = reqeust.POST.get("userPw")
    # id = constants.DEMO_LOGINID
    # pw = constants.DEMO_LOGINPASSWORD


    # 4-5
    # 접속할 서버 주소 설정
    # 접속할 서버의 기본 주소는 'hts.ebestsec.co.kr'인데 모의 투자인 경우에는 'demo.ebestsec.co.kr'을 사용

        # 4-5-1
        # 본 서버
    instXASession.ConnectServer("hts.ebestsec.co.kr", constants.SERVER_PORT)
    instXASession.Login(user_id, user_pw, cert_pw, constants.SERVER_PORT, 0)
    
        # 4-5-2
        # 모의거래 서버
    # instXASession.ConnectServer("demo.ebestsec.co.kr", 20001)
    # instXASession.Login(id, pw, 0, 0)


    # 4-6
    # 로그인 성공 시 까지 웨이팅 시키는 while문
    while constants.LOGINSTATE == False:
        pythoncom.PumpWaitingMessages()


    # 4-7
    # Session에 접속자 정보 등록시키기
    if constants.LOGINSTATE == True:
        reqeust.session['user_id'] = user_id
        reqeust.session['user_pw'] = user_pw
        # 4-8
        # True로 변한 데이터를 원복 시키기
        constants.LOGINSTATE == False
        return HttpResponse(reqeust, )
    return False





