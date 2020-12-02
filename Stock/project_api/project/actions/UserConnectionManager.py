from core.constants import *
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client as win_client
import pythoncom

from project.eventhandler.XASessionEventHandler import XASessionEventHandler
from project.eventhandler.XAQueryEventHandlerT0424 import XAQueryEventHandlerT0424
from project.eventhandler.XAQueryEventHandlerT4201 import XAQueryEventHandlerT4201
from project.eventhandler.XAQueryEventHandlerT8407 import XAQueryEventHandlerT8407
from project.eventhandler.XAQueryEventHandlerT8430 import XAQueryEventHandlerT8430

class XAConnector:
    xa_session = None
    ebest_id = None
    ebest_pw = None
    ebest_cpwd = None
    account_list = []
    ebest_address = None
    ebest_port = None
    # def __init__(self):
    #     self.xa_session = None
 
    def connect_server(self):
        if self.xa_session is None or XAConnector.ebest_address is None:
            pythoncom.CoInitialize()
            self.xa_session = win_client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)
            pythoncom.CoUninitialize()
            XAConnector.ebest_address = DEMO_SERVER
            XAConnector.ebest_port = SERVER_PORT
        return self.xa_session.ConnectServer(XAConnector.ebest_address, XAConnector.ebest_port)

    def is_connected(self):
        if self.xa_session is None:
            result = False
        else:
            result = self.xa_session.IsConnected()
            return result
 
    def login(self, user_id, user_pw, user_cpwd):
        if XASessionEventHandler.login_flag :
            return XASessionEventHandler.login_flag

        XAConnector.ebest_id = user_id
        XAConnector.ebest_pw = user_pw
        XAConnector.ebest_cpwd = user_cpwd
        if XAConnector.ebest_id == None or XAConnector.ebest_pw == None: 
            return ValueError
        else: 
            self.xa_session.Login(XAConnector.ebest_id, XAConnector.ebest_pw, XAConnector.ebest_cpwd, 0, 0)
        
        # 로그인 성공 시 까지 웨이팅 시키는 while문
        while XASessionEventHandler.login_flag == False:
            pythoncom.PumpWaitingMessages()
        XASessionEventHandler.login_flag = False
        return XASessionEventHandler.login_flag
 
    def get_account_list(self):
        
        account_ctn = self.xa_session.GetAccountListCount()
 
        for i in range(account_ctn):
            account_num = self.xa_session.GetAccountList(i)
            XAConnector.account_list.append(account_num)
        
        return XAConnector.account_list
 
    def disconnect_server(self):
        self.xa_session.DisconnectServer()
        self.xa_session = None
        XAConnector.ebest_id = None
        XAConnector.ebest_pw = None
        XAConnector.ebest_cpwd = None
        XAConnector.account_list = []
        XAConnector.ebest_address = None
        XAConnector.ebest_port = None

    def userDataSearch(self, request, accountNum, accountPw):
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector))
        # TODO Print 지우기
        if XAConnector.is_connected(XAConnector) == False:
            XAConnector.connect_server(XAConnector)
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        instXAQueryT0424 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        instXAQueryT0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"

        # 서버에 request보낼 데이터 세팅하기
        # DevCenter1을 열어보면 InBlock에는 데이터를 넣어주어야하는 목록이 적혀있다. 여기에 데이터를 넣어줄 때는 SetFieldData를 쓴다.
        # 파라미터는 1. 블럭명, 2. 요소명, 3. 단일데이터인지 멀티데이터인지 구분(단일이면 0), 4. 집어넣을 값 
        instXAQueryT0424.SetFieldData("t0424InBlock", "accno", 0, accountNum) # 계좌정보
        instXAQueryT0424.SetFieldData("t0424InBlock", "passwd", 0, accountPw)  # 비밀번호
        instXAQueryT0424.SetFieldData("t0424InBlock", "prcgb", 0, 1)          # 단가 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "chegb", 0, 0)          # 체결 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "dangb", 0, 0)          # 단일가 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "charge", 0, 1)          # 제비용 포함여부
        instXAQueryT0424.SetFieldData("t0424InBlock", "cts_expcode", 0, " ")          # CTS 종목번호

        # 입력한 데이터로 서버에 request요청
        instXAQueryT0424.Request(0)
        # 응답이 올 때까지 대기
        while XAQueryEventHandlerT0424.data_flag == False:
            pythoncom.PumpWaitingMessages()

        # Response된 응답을 이용해 원하는 데이터 추출하기
        estimatedNetWorth = instXAQueryT0424.GetFieldData("t0424OutBlock", "sunamt", 0)                     # 추정 순자산
        totalPrice = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mamt", 0)                             # 매입금액
        evaluationPNL = instXAQueryT0424.GetFieldData("t0424OutBlock1", "tdtsunik", 0)                      # 평가손익
        

        evaluationRateOfReturnByStock = ""
        if estimatedNetWorth != None and estimatedNetWorth != "" and totalPrice != None and totalPrice != "" and  evaluationPNL != None and evaluationPNL != "":
            evaluationRateOfReturnByStock =  round((int(evaluationPNL) / int(totalPrice)), 1)                # 평가 수익율
            
            
        realProfit = instXAQueryT0424.GetFieldData("t0424OutBlock", "dtsunik", 0)                           # 실현손익
        

        realRateOfReturnByStock = ""
        if estimatedNetWorth != None and estimatedNetWorth != "" and realProfit != None and realProfit != "":
            realRateOfReturnByStock = round((int(realProfit) / (int(realProfit) + int(estimatedNetWorth))), 1)  # 실현 수익율
            

        userData = {
            'estimatedNetWorth' : estimatedNetWorth,
            'totalPrice' : totalPrice,
            'evaluationPNL' : evaluationPNL,
            'evaluationRateOfReturnByStock' : evaluationRateOfReturnByStock,
            'realProfit' : realProfit,
            'realRateOfReturnByStock' : realRateOfReturnByStock
        }
        
        XAQueryEventHandlerT0424.data_flag = False
        request.session['user_data'] = userData
        return userData


    def stockSearch(self, stockCategory):
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector))
        # TODO Print 지우기
        if XAConnector.is_connected(XAConnector) == False:
            XAConnector.connect_server(XAConnector)
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        instXAQueryT8430 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT8430)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        instXAQueryT8430.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t8430.res"

        # 서버에 request보낼 데이터 세팅하기
        instXAQueryT8430.SetFieldData("t8430InBlock", "gubun", 0, stockCategory) # 주식 카테고리 선택(0 : 전체, 1: 코스피, 2: 코스닥)


        # 입력한 데이터로 서버에 request요청
        instXAQueryT8430.Request(0)

        # 응답이 올 때까지 대기
        while XAQueryEventHandlerT8430.data_flag == False:
            pythoncom.PumpWaitingMessages()

        # 전체 데이터가 몇개인지 체크
        count = instXAQueryT8430.GetBlockCount("t8430OutBlock")

        # 내보낼 데이터 목록
        stockList = []

        # 원하는 만큼 데이터 추출하기
        for i in range(count):
            hname = instXAQueryT8430.GetFieldData("t8430OutBlock", "hname", i)   # 종목명
            shcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "shcode", i)   # 단축코드
            recprice = instXAQueryT8430.GetFieldData("t8430OutBlock", "recprice", i)   # 기준가
            uplmtprice = instXAQueryT8430.GetFieldData("t8430OutBlock", "uplmtprice", i)   # 상한가
            dnlmtprice = instXAQueryT8430.GetFieldData("t8430OutBlock", "dnlmtprice", i)   # 하한가
            stock = {'hname' : hname, 'shcode' : shcode, 'recprice' : recprice, 'uplmtprice' : uplmtprice, 'dnlmtprice' : dnlmtprice}
            # expcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "expcode", 0)   # 확장코드
            # etfgubun = instXAQueryT8430.GetFieldData("t8430OutBlock", "etfgubun", 0)   # ETF구분
            # jnilclose = instXAQueryT8430.GetFieldData("t8430OutBlock", "jnilclose", 0)   # 전일가
            # memedan = instXAQueryT8430.GetFieldData("t8430OutBlock", "memedan", 0)   # 주문수량단위
            stockList.append(stock)

        XAQueryEventHandlerT8430.data_flag = False
        return stockList


    def stockChart(self, shcode, gubun, ncnt, qrycnt, sdate, edate):
        # TODO Print 지우기
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector))
        if XAConnector.is_connected(XAConnector) == False:
            XAConnector.connect_server(XAConnector)
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        instXAQueryT4201 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT4201)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        instXAQueryT4201.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t4201.res"

        
        # 서버에 request보낼 데이터 세팅하기
        # 종목명
        instXAQueryT4201.SetFieldData("t4201InBlock", "shcode", 0, shcode)
        # 봉구분(0: 틱봉, 1:분봉, 2: 일봉, 3: 주봉, 4: 월봉)
        instXAQueryT4201.SetFieldData("t4201InBlock", "gubun", 0, gubun)
        # 봉 단위(gubun이 1이면서 ncnt가 1이면 1분봉 단위로, 2면 2분봉 단위로 30이면 30분봉 단위로 보여줌)
        instXAQueryT4201.SetFieldData("t4201InBlock", "ncnt", 0, ncnt)
        # 봉의 개수 (최대 몇개 노출시킬 것인지 결정 => 1 ~ 500까지만 유효)
        instXAQueryT4201.SetFieldData("t4201InBlock", "qrycnt", 0, qrycnt)
        # 일자 기준 (0: 전체일자, 1: 오늘만 => 전체를 사용할 예정)
        instXAQueryT4201.SetFieldData("t4201InBlock", "tdgb", 0, 0)
        # 시작일, 종료일(최소 일봉부터 이 내용이 적용됌 틱봉, 분봉은 이 내용이 적용되지 않으므로 주의 필요)
        instXAQueryT4201.SetFieldData("t4201InBlock", "sdate", 0, sdate)
        instXAQueryT4201.SetFieldData("t4201InBlock", "edate", 0, edate)
        # 아래는 기본설정을 이용하면 됌
        instXAQueryT4201.SetFieldData("t4201InBlock", "cts_date", 0, " ")
        instXAQueryT4201.SetFieldData("t4201InBlock", "cts_time", 0, " ")
        instXAQueryT4201.SetFieldData("t4201InBlock", "cts_daygb", 0, " ")


        # 입력한 데이터로 서버에 request요청
        instXAQueryT4201.Request(0)

        # 응답이 올 때까지 대기
        while XAQueryEventHandlerT4201.data_flag == False:
            pythoncom.PumpWaitingMessages()

        # 내보낼 데이터 목록
        stockDetailList = []

        # 전체 데이터가 몇개인지 체크
        count = int(qrycnt)
        # 원하는 만큼 데이터 추출하기
        for i in range(count):
            stock_date = instXAQueryT4201.GetFieldData("t4201OutBlock1", "date", i)             # 날짜
            stock_time = instXAQueryT4201.GetFieldData("t4201OutBlock1", "time", i)             # 시간
            stock_open = instXAQueryT4201.GetFieldData("t4201OutBlock1", "open", i)             # 시가
            stock_high = instXAQueryT4201.GetFieldData("t4201OutBlock1", "high", i)             # 고가
            stock_low = instXAQueryT4201.GetFieldData("t4201OutBlock1", "low", i)               # 저가
            stock_close = instXAQueryT4201.GetFieldData("t4201OutBlock1", "close", i)           # 종가
            stock_jdiff_vol = instXAQueryT4201.GetFieldData("t4201OutBlock1", "jdiff_vol", i)   # 거래량
            # stock_value = instXAQueryT4201.GetFieldData("t4201OutBlock1", "value", i)           # 거래대금
            # stock_jongchk = instXAQueryT4201.GetFieldData("t4201OutBlock1", "jongchk", i)       # 수정구분
            # stock_rate = instXAQueryT4201.GetFieldData("t4201OutBlock1", "rate", i)             # 수정비율
            # stock_pricechk = instXAQueryT4201.GetFieldData("t4201OutBlock1", "pricechk", i)     # 수정주가반영항목
            # stock_ratevalue = instXAQueryT4201.GetFieldData("t4201OutBlock1", "ratevalue", i)   # 수정비율반영거래대금
            if stock_date == "" :
                break
            stock_detail = {'stock_date' : stock_date, 'stock_time' : stock_time, 'stock_open' : stock_open, 'stock_high' : stock_high, 'stock_low' : stock_low, 'stock_close' : stock_close, 'stock_jdiff_vol' : stock_jdiff_vol}
            stockDetailList.append(stock_detail)

        XAQueryEventHandlerT4201.data_flag = False

        return stockDetailList