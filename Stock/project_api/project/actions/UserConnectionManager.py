from core import constants
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client as win_client
import pythoncom

from project.actions import UserLogin

class XAConnector:
    xa_session = None

    # def __init__(self):
    #     self.xa_session = None
 
    def connect_server(self):
        if self.xa_session is None:
            pythoncom.CoInitialize()
            self.xa_session = win_client.DispatchWithEvents("XA_Session.XASession", UserLogin.XASessionEventHandler)
            pythoncom.CoUninitialize()
            ebest_address = constants.DEMO_SERVER
            ebest_port = constants.SERVER_PORT
            print("포트번호? : ", ebest_port)
        return self.xa_session.ConnectServer(ebest_address, ebest_port)

    def is_connected(self):
        if self.xa_session is None:
            result = False
        else:
            result = self.xa_session.IsConnected()
            print("IsConnected()값이 대체 뭐냐? : ", result)
        return result
 
    def login(self):
        if constants.LOGINSTATE:
            return constants.LOGINSTATE
        ebest_id = constants.LOGINID
        ebest_pw = constants.LOGINPASSWORD
        ebest_cpwd = constants.LOGINCERTPASSWORD
        if ebest_id == "" or ebest_pw == "" or ebest_cpwd == "" or ebest_id == None or ebest_pw == None or ebest_cpwd == None: 
            print("세션이 종료되었습니다. 로그인 페이지로 이동합니다.")
            return False
        else: 
            self.xa_session.Login(ebest_id, ebest_pw, ebest_cpwd, 0, 0)
        
        # 로그인 성공 시 까지 웨이팅 시키는 while문
        while constants.LOGINSTATE == False:
            pythoncom.PumpWaitingMessages()

        return constants.LOGINSTATE
 
    def get_account_list(self):
        account_list = []
        account_ctn = self.xa_session.GetAccountListCount()
 
        for i in range(account_ctn):
            account_num = self.xa_session.GetAccountList(i)
            account_list.append(account_num)
        return account_list
 
    def disconnect_server(self):
        if constants.LOGINSTATE:
            self.xa_session.DisconnectServer()
            constants.LOGINSTATE = False