import win32com.client
import pythoncom
from django.http import HttpResponseRedirect,HttpResponse
from core import constants
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
from project.actions import UserConnectionManager

# 3. 로그인이벤트 처리 클래스 구현
class XASessionEventHandler:
    def OnLogin(self, code, msg):
        print("OnLogin 실행 =======================")
        if code == '0000':
            print("\nLogin성공 =======================\nmsg : ", msg, "\ncode : ", code, "\n")
            constants.LOGINSTATE = True
        else :
            print("로그인 실패")
            XASessionEventHandler.OnDisconnect(self, code, msg)
    def OnDisconnect(self, code, msg):
        print("\nOnDisconnect 실행 =======================\nmsg : ", msg, "\ncode : ", code, "\n")
        constants.LOGINSTATE = False 
        return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '아이디 또는 패스워드를 확인하세요'}))




# 4. 로그인 기능
def doLogin(reqeust):
    print("doLogin 실행 =======================")
    XAConnector = UserConnectionManager.XAConnector()
    # 이미 로그인 했는지 체크
    data = {}
    # 4-1
    # COM을 사용하기 위해 라이브러리 초기화
    # 서브 스레드에서 COM 객체를 사용하려면 COM 라이브러리를 초기화 해야함
    # pythoncom.CoInitialize()

    # 4-2
    # XASession 클래스에 대한 인스턴스를 생성 
    # DispatchWithEvents 함수의 첫 번째 인자로는 인스턴스를 생성하려는 클래스의 이름을 지정하면 됩니다. 
    # XASession 클래스는 XA_Session.dll이라는 파일에 구현돼 있으므로 'XA_Session.XASession'을 입력했습니다.
    # instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)
    # 4-3
    # COM을 사용 후 라이브러리 초기화
    # pythoncom.CoUninitialize()


    # 4-4
    # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
    if reqeust.method == 'POST':
        constants.LOGINID = reqeust.POST.get("userId")
        constants.LOGINPASSWORD = reqeust.POST.get("userPw")
        constants.LOGINCERTPASSWORD = reqeust.POST.get("userCertPassword")
    user_id = constants.LOGINID
    user_pw = constants.LOGINPASSWORD
    cert_pw = constants.LOGINCERTPASSWORD 
    

    # 4-5
    # 접속할 서버 주소 설정
    # 접속할 서버의 기본 주소는 'hts.ebestsec.co.kr'인데 모의 투자인 경우에는 'demo.ebestsec.co.kr'을 사용

        # 4-5-1
        # 본 서버
    # instXASession.ConnectServer(constants.MAIN_SERVER, constants.SERVER_PORT)
    # instXASession.Login(user_id, user_pw, cert_pw, constants.SERVER_PORT, 0)
    
        # 4-5-2
        # 모의거래 서버
    # instXASession.ConnectServer(constants.DEMO_SERVER, constants.SERVER_PORT)
    # 4-6
    # 로그인 성공 시 까지 웨이팅 시키는 while문
    # while constants.LOGINSTATE == False:
    #     pythoncom.PumpWaitingMessages()

    # 4-7
    # 내 계좌 개수 조회
    # num_account = instXASession.GetAccountListCount()
    # accounts = []
    # for i in range(num_account):
        # 유저 전체 계좌 번호 조회해 가져오기
        # account = instXASession.GetAccountList(i)
        # print("account 번호 : ", account)
        # accounts.append(account)
        # print("accounts들 : ", accounts)
    if XAConnector.is_connected() == False:
        try:
            print("로그인할 유저아이디 : ", constants.LOGINID)
            XAConnector.connect_server()
            XAConnector.login()
            reqeust.session['user_id'] = user_id
            reqeust.session['accounts'] = XAConnector.get_account_list()
        except:
            print("로그인 처리 중 에러가 발생하였습니다.")
            return HttpResponse(json.dumps({'status' : 'FAIL'}))
    
    data = {
        'user_id' : reqeust.session.get('user_id'),
        'accounts' : reqeust.session.get('accounts')
    }

    print("로그인 판단 부분 종료 : ", data)

    # 4-9
    # True로 변한 데이터를 원복 시키기
    constants.LOGINSTATE == False
    return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))




