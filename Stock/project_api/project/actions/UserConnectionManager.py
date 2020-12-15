from core.constants import *
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client as win_client
import pythoncom
from pandas import Series, DataFrame
import time

from project.eventhandler.XASessionEventHandler import XASessionEventHandler
from project.eventhandler.XAQueryEventHandlerT0424 import XAQueryEventHandlerT0424
from project.eventhandler.XAQueryEventHandlerT1452 import XAQueryEventHandlerT1452
from project.eventhandler.XAQueryEventHandlerT4201 import XAQueryEventHandlerT4201
from project.eventhandler.XAQueryEventHandlerT8407 import XAQueryEventHandlerT8407
from project.eventhandler.XAQueryEventHandlerT8430 import XAQueryEventHandlerT8430
from project.eventhandler.XAQueryEventHandlerCSPAT00600 import XAQueryEventHandlerCSPAT00600
from project.eventhandler.XAQueryEventHandlerCSPAQ13700 import XAQueryEventHandlerCSPAQ13700

class XAConnector:
    xa_session = None
    ebest_id = None
    ebest_pw = None
    ebest_cpwd = None
    account_list = []
    ebest_address = None
    ebest_port = None
    typeOfStockData = None
    stock_lists = None
    stock_lists_code = None
    # def __init__(self):
    #     self.xa_session = None
 
    def connect_server(self):
        print('서버연결 시도합니다.\n     self.xa_session: ', self.xa_session, '\n     XAConnector.ebest_address: ', XAConnector.ebest_address, '\n     XAConnector.is_connected: ', XAConnector.is_connected(XAConnector))
        if self.xa_session is None or XAConnector.ebest_address is None or XAConnector.is_connected(XAConnector) is None:
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
    
    def logout(self):
        self.xa_session.Logout()
        XAConnector.disconnect_server(self)

    def login(self, user_id, user_pw, user_cpwd):
        XAConnector.ebest_id = user_id
        XAConnector.ebest_pw = user_pw
        XAConnector.ebest_cpwd = user_cpwd
        if XAConnector.ebest_id == None or XAConnector.ebest_pw == None: 
            return ValueError
        else: 
            self.xa_session.Login(XAConnector.ebest_id, XAConnector.ebest_pw, XAConnector.ebest_cpwd, 0, 0)
        
        # 응답이 올 때까지 대기
        print("XASession 응답 대기 : ", XASessionEventHandler.data_flag)
        result = XAConnector.watting(XAConnector, XASessionEventHandler)
        print("XASession 응답 결과 : ", result)
        if result == TimeoutError:
            return TimeoutError

        XASessionEventHandler.login_flag = False

        return XASessionEventHandler.login_flag
 
    def get_account_list(self):
        
        account_ctn = self.xa_session.GetAccountListCount()
 
        for i in range(account_ctn):
            account_num = self.xa_session.GetAccountList(i)
            XAConnector.account_list.append(account_num)
        
        return XAConnector.account_list
 
    def disconnect_server(self):
        try:
            XAConnector.ebest_id = None
            XAConnector.ebest_pw = None
            XAConnector.ebest_cpwd = None
            XAConnector.account_list = []
            XAConnector.ebest_address = None
            XAConnector.ebest_port = None
            self.xa_session = None
        except Exception as e:
            print(e)
            return False
        return True
    
    def watting(self, handler):
            start = time.time()
            print("핸들러 명 : ", handler, "\n시작 시간: ", start)
            while handler.data_flag == False:
                pythoncom.PumpWaitingMessages()
                time.sleep(0.001)
                # end = time.time()
                # now_time = end - start
                # if (now_time) >= 30:
                #     return TimeoutError
            return XAConnector.data_flag_tune(self, handler)

    def data_flag_tune(self, handler):
        handler.data_flag = False
        return True

    def user_data_search(self, account_num, account_pw, is_continue):
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector))
        if XAConnector.is_connected(XAConnector) == None:
            return ConnectionRefusedError
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_t0424 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_t0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"
        
        # 서버에 request보낼 데이터 세팅하기
        # DevCenter1을 열어보면 InBlock에는 데이터를 넣어주어야하는 목록이 적혀있다. 여기에 데이터를 넣어줄 때는 SetFieldData를 쓴다.
        # 파라미터는 1. 블럭명, 2. 요소명, 3. 단일데이터인지 멀티데이터인지 구분(단일이면 0), 4. 집어넣을 값 
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "accno", 0, account_num) # 계좌정보
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "passwd", 0, account_pw)  # 비밀번호
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "prcgb", 0, 1)          # 단가 구분
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "chegb", 0, 0)          # 체결 구분
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "dangb", 0, 0)          # 단일가 구분
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "charge", 0, 1)          # 제비용 포함여부
        inst_xaquery_t0424.SetFieldData("t0424InBlock", "cts_expcode", 0, " ")          # CTS 종목번호

        # 입력한 데이터로 서버에 request요청
        inst_xaquery_t0424.Request(is_continue)
            
        # 응답이 올 때까지 대기
        print("T0424 응답 대기 : ", XAQueryEventHandlerT0424.data_flag)
        result = XAConnector.watting(XAConnector, XAQueryEventHandlerT0424)
        print("T0424 응답 결과 : ", result)
        if result == TimeoutError:
            return result

        # Response된 응답을 이용해 원하는 데이터 추출하기
        estimated_net_worth = inst_xaquery_t0424.GetFieldData("t0424OutBlock", "sunamt", 0)                     # 추정 순자산
        user_property = estimated_net_worth

        # 보유종목을 담아줄 리스트
        retained_item_list = []

        # 전체 데이터 개수 체크
        retained_item_list_length = inst_xaquery_t0424.GetBlockCount("t0424OutBlock1")
        for i in range(retained_item_list_length):
            expcode = inst_xaquery_t0424.GetFieldData("t0424OutBlock1", "expcode", i)  # 종목번호
            if (expcode == "") :
                break
            hname = inst_xaquery_t0424.GetFieldData("t0424OutBlock1", "hname", i)      # 종목명
            price = inst_xaquery_t0424.GetFieldData("t0424OutBlock1", "price", i)      # 현재가
            mdposqt = inst_xaquery_t0424.GetFieldData("t0424OutBlock1", "mdposqt", i)  # 매도가능수량
            sunikrt = inst_xaquery_t0424.GetFieldData("t0424OutBlock1", "sunikrt", i)  # 수익률
            retained_item = {
                'expcode': expcode,
                'hname': hname,
                'price': price,
                'mdposqt': mdposqt,
                'sunikrt': sunikrt
            }
            retained_item_list.append(retained_item)
        
        print("유저 보유종목은? : ", retained_item_list)
        return [user_property, retained_item_list]


    def stock_search(self, stock_category, is_continue):
        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_t8430 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT8430)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_t8430.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t8430.res"
        # 서버에 request보낼 데이터 세팅하기
        inst_xaquery_t8430.SetFieldData("t8430InBlock", "gubun", 0, stock_category) # 주식 카테고리 선택(0 : 전체, 1: 코스피, 2: 코스닥)
        
        # 입력한 데이터로 서버에 request요청
        req_number = inst_xaquery_t8430.Request(is_continue)
        print("요청 성공 유무? : ", req_number)
        # 응답이 올 때까지 대기
        print("T8430 응답 대기 : ", XAQueryEventHandlerT8430.data_flag)
        result = XAConnector.watting(XAConnector, XAQueryEventHandlerT8430)
        print("T8430 응답 결과 : ", result)
        if result == TimeoutError:
            return result
        # 내보낼 데이터 목록
        stock_list = []

        # 전체 데이터가 몇개인지 체크
        count = inst_xaquery_t8430.GetBlockCount("t8430OutBlock")

        # 원하는 만큼 데이터 추출하기
        for i in range(count):
            hname = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "hname", i)   # 종목명
            shcode = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "shcode", i)   # 단축코드
            recprice = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "recprice", i)   # 기준가
            uplmtprice = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "uplmtprice", i)   # 상한가
            dnlmtprice = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "dnlmtprice", i)   # 하한가
            stock = {'hname' : hname, 'shcode' : shcode, 'recprice' : recprice, 'uplmtprice' : uplmtprice, 'dnlmtprice' : dnlmtprice}
            # expcode = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "expcode", 0)   # 확장코드
            # etfgubun = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "etfgubun", 0)   # ETF구분
            # jnilclose = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "jnilclose", 0)   # 전일가
            # memedan = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "memedan", 0)   # 주문수량단위
            stock_list.append(stock)

        print("종목 조회 완료되었습니다. =========================================================")
        XAConnector.stock_lists = stock_list
        XAConnector.stock_lists_code = stock_category
        return stock_list


    def stock_chart(self, shcode, gubun, ncnt, qrycnt, sdate, edate, is_continue):
        # TODO Print 지우기
        if XAConnector.is_connected(XAConnector) == None:
            return ConnectionRefusedError
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_t4201 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT4201)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_t4201.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t4201.res"


        # 데이터 단일조회인지 연속
        if is_continue :
            # 서버에 request보낼 데이터 세팅하기
            # 종목명
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "shcode", 0, shcode)
            # 봉구분(0: 틱봉, 1:분봉, 2: 일봉, 3: 주봉, 4: 월봉)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "gubun", 0, gubun)
            # 봉 단위(gubun이 1이면서 ncnt가 1이면 1분봉 단위로, 2면 2분봉 단위로 30이면 30분봉 단위로 보여줌)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "ncnt", 0, ncnt)
            # 봉의 개수 (최대 몇개 노출시킬 것인지 결정 => 1 ~ 500까지만 유효)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "qrycnt", 0, qrycnt)
            # 일자 기준 (0: 전체일자, 1: 오늘만 => 전체를 사용할 예정)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "tdgb", 0, 0)
            # 시작일, 종료일(최소 일봉부터 이 내용이 적용됌 틱봉, 분봉은 이 내용이 적용되지 않으므로 주의 필요)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "sdate", 0, sdate)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "edate", 0, edate)
            # 아래는 기본설정을 이용하면 됌
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_date", 0, " ")
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_time", 0, " ")
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_daygb", 0, " ")

            # 입력한 데이터로 서버에 request요청
            inst_xaquery_t4201.Request(True)

            # 응답이 올 때까지 대기
            print("T4201 응답 대기 : ", XAQueryEventHandlerT4201.data_flag)
            result = XAConnector.watting(XAConnector, XAQueryEventHandlerT4201)
            print("T4201 응답 결과 : ", result)
            if result == TimeoutError:
                return TimeoutError
            
        else :
            # 서버에 request보낼 데이터 세팅하기
            # 종목명
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "shcode", 0, shcode)
            # 봉구분(0: 틱봉, 1:분봉, 2: 일봉, 3: 주봉, 4: 월봉)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "gubun", 0, gubun)
            # 봉 단위(gubun이 1이면서 ncnt가 1이면 1분봉 단위로, 2면 2분봉 단위로 30이면 30분봉 단위로 보여줌)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "ncnt", 0, ncnt)
            # 봉의 개수 (최대 몇개 노출시킬 것인지 결정 => 1 ~ 500까지만 유효)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "qrycnt", 0, qrycnt)
            # 일자 기준 (0: 전체일자, 1: 오늘만 => 전체를 사용할 예정)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "tdgb", 0, 0)
            # 시작일, 종료일(최소 일봉부터 이 내용이 적용됌 틱봉, 분봉은 이 내용이 적용되지 않으므로 주의 필요)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "sdate", 0, sdate)
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "edate", 0, edate)
            # 아래는 기본설정을 이용하면 됌
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_date", 0, " ")
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_time", 0, " ")
            inst_xaquery_t4201.SetFieldData("t4201InBlock", "cts_daygb", 0, " ")

            # 입력한 데이터로 서버에 request요청
            inst_xaquery_t4201.Request(0)

            # 응답이 올 때까지 대기
            print("T4201 응답 대기 : ", XAQueryEventHandlerT4201.data_flag)
            result = XAConnector.watting(XAConnector, XAQueryEventHandlerT4201)
            print("T4201 응답 결과 : ", result)
            if result == TimeoutError:
                return TimeoutError

        # 내보낼 데이터 목록
        stock_detail_list = []

        # 전체 데이터가 몇개인지 체크
        count = int(qrycnt)
        # 원하는 만큼 데이터 추출하기
        for i in range(count):
            stock_date = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "date", i)             # 날짜
            stock_time = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "time", i)             # 시간
            stock_open = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "open", i)             # 시가
            stock_high = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "high", i)             # 고가
            stock_low = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "low", i)               # 저가
            stock_close = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "close", i)           # 종가
            stock_jdiff_vol = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "jdiff_vol", i)   # 거래량
            # stock_value = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "value", i)           # 거래대금
            # stock_jongchk = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "jongchk", i)       # 수정구분
            # stock_rate = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "rate", i)             # 수정비율
            # stock_pricechk = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "pricechk", i)     # 수정주가반영항목
            # stock_ratevalue = inst_xaquery_t4201.GetFieldData("t4201OutBlock1", "ratevalue", i)   # 수정비율반영거래대금
            if stock_date == "" :
                break
            
            stock_detail = {'stock_date' : stock_date[0:4] + '-' + stock_date[4:6] + '-' + stock_date[6:8], 'stock_time' : stock_time, 'stock_low' : stock_low, 'stock_open' : stock_open, 'stock_close' : stock_close, 'stock_high' : stock_high, 'stock_jdiff_vol' : stock_jdiff_vol}
            stock_detail_list.append(stock_detail)

        return stock_detail_list

    
    def stock_tradding(self, acnt_no, input_pw, isu_no, ord_qty, ord_prc, bns_tp_code, ordprc_ptn_code):
        # TODO Print 지우기
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector), '데이터들 : ', acnt_no, input_pw, isu_no, ord_qty, ord_prc, bns_tp_code, ordprc_ptn_code)
        if XAConnector.is_connected(XAConnector) == None:
            return ConnectionRefusedError
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_cspat00600 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerCSPAT00600)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_cspat00600.ResFileName = "C:\\eBEST\\xingAPI\\Res\\CSPAT00600.res"

        # input할 데이터 정리
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "AcntNo", 0, acnt_no)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "InptPwd", 0, input_pw)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "IsuNo", 0, isu_no)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "OrdQty", 0, ord_qty)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, ord_prc)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, bns_tp_code)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "OrdprcPtnCode", 0, ordprc_ptn_code)
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "MgntrnCode", 0, '000')
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "LoanDt", 0, "")
        inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "OrdCndiTpCode", 0, '0')
        
        # 입력한 데이터로 서버에 request요청
        inst_xaquery_cspat00600.Request(0)

        # 응답이 올 때까지 대기
        print("CSPAT00600 응답 대기 : ", XAQueryEventHandlerCSPAT00600.data_flag)
        result = XAConnector.watting(XAConnector, XAQueryEventHandlerCSPAT00600)
        print("CSPAT00600 응답 결과 : ", result)
        if result == TimeoutError:
            return TimeoutError

        # 원하는 데이터 받기

        mbr_no = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "MbrNo", 0)
        acnt_no = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "AcntNo", 0)
        isu_no = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "IsuNo", 0)
        ord_prc = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "OrdPrc", 0)
        ord_qty = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "OrdQty", 0)
        bns_tp_code = inst_xaquery_cspat00600.GetFieldData("CSPAT00600OutBlock1", "BnsTpCode", 0)

        # TODO 
        # 추후 운용관리가 용의하도록 위 데이터들을 디비에 저장

        # 데이터 보내기
        data = {'MbrNo': mbr_no, 'AcntNo': acnt_no, 'IsuNo': isu_no, 'OrdPrc': ord_prc, 'OrdQty': ord_qty, 'BnsTpCode': bns_tp_code}
        print('조회완료 : ', data)

        return data

    
    def stockTraddingState(self, acnt_no, input_pw, isu_no, ord_dt):
        # TODO Print 지우기
        print("접속상태 확인 : ", XAConnector.is_connected(XAConnector), '데이터들 : ', acnt_no, input_pw, isu_no, ord_dt)
        if XAConnector.is_connected(XAConnector) == None:
            return ConnectionRefusedError
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_cspaq13700 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerCSPAQ13700)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_cspaq13700.ResFileName = "C:\\eBEST\\xingAPI\\Res\\CSPAQ13700.res"

        # input할 데이터 정리 => 그냥 입력되어 있는 내용은 전체 출력을 하겠다는 의미
        count = 500
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "RecCnt", 0, count)          # 레코드 개수
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "AcntNo", 0, acnt_no)       # 계좌번호
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "InptPwd", 0, input_pw)     # 입력비밀번호
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "OrdMktCode", 0, 00)       # 주문시장코드
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "BnsTpCode", 0, 0)         # 매매구분
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "IsuNo", 0, 'A'+isu_no)     # 종목번호 => A는 주식을 의미
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "ExecYn", 0, 0)            # 체결여부
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "OrdDt", 0, ord_dt)         # 주문일 
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "SrtOrdNo2", 0, 000000000) # 시작주문번호 : 정순
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "BkseqTpCode", 0, 1)       # 역순구분 : 정순
        inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "OrdPtnCode", 0, 00)       # 주문유형코드
        
        # 입력한 데이터로 서버에 request요청
        inst_xaquery_cspaq13700.Request(0)

        # 응답이 올 때까지 대기
        print("CSPAQ13700 응답 대기 : ", XAQueryEventHandlerCSPAQ13700.data_flag)
        result = XAConnector.watting(XAConnector, XAQueryEventHandlerCSPAQ13700)
        print("CSPAQ13700 응답 결과 : ", result)
        if result == TimeoutError:
            return TimeoutError

        # 원하는 데이터 받기
        tradding_list = []
        for i in range(count):
            stock_bns_tp_nm = inst_xaquery_cspaq13700.GetFieldData("CSPAQ13700OutBlock3", "BnsTpNm", i)      # 매매구분
            if stock_bns_tp_nm == "":
                break
            stock_ord_qty = inst_xaquery_cspaq13700.GetFieldData("CSPAQ13700OutBlock3", "OrdQty", i)        # 주문수량
            stock_ord_prc = inst_xaquery_cspaq13700.GetFieldData("CSPAQ13700OutBlock3", "OrdPrc", i)        # 주문가격
            stock_exec_qty = inst_xaquery_cspaq13700.GetFieldData("CSPAQ13700OutBlock3", "ExecQty", i)      # 체결수량
            stock_exec_prc = inst_xaquery_cspaq13700.GetFieldData("CSPAQ13700OutBlock3", "ExecPrc", i)      # 체결가격
            if stock_ord_qty == '':
                stock_ord_qty = 0
            if stock_exec_qty == '':
                stock_exec_qty = 0
            stock_non_exec_qty = int(stock_ord_qty) - int(stock_exec_qty)                                      # 미체결량
            data = {'stockBnsTpNm': stock_bns_tp_nm, 'stockOrdQty': stock_ord_qty, 'stockOrdPrc': stock_ord_prc, 'stockExecQty': stock_exec_qty, 'stockExecPrc': stock_exec_prc, 'stockNonExecQty': stock_non_exec_qty}
            tradding_list.append(data)
        
        print(tradding_list)

        return tradding_list



    def high_volume_stock_search(self):
        time.sleep(1)
        # TODO Print 지우기
        print("high_volume_stock_search 접속상태 확인 : ", XAConnector.is_connected(XAConnector))
        print("API상태 확인 : ", self.xa_session.IsLoadAPI())
        if XAConnector.is_connected(XAConnector) == None:
            return ConnectionRefusedError
        

        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        inst_xaquery_t1452 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT1452)
        pythoncom.CoUninitialize()

        # 가져올 데이터가 들어있는 res파일 생성해주기
        inst_xaquery_t1452.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1452.res"

        # input할 데이터 정리 => 그냥 입력되어 있는 내용은 전체 출력을 하겠다는 의미
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "gubun", 0, "0")                  # 구분(전체)
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "jnilgubun", 0, "1")              # 전일구분(당일)
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "sdiff", 0, "1")                 # 시작등락율
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "ediff", 0, "100000")                 # 종료등락율
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "jc_num", 0, "000000000768")    # 대상 제외
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "sprice", 0, "1")                # 시작 가격
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "eprice", 0, "10000000000")                # 종료 가격
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "volume", 0, "15000000")          # 거래량
        inst_xaquery_t1452.SetFieldData("t1452InBlock", "idx", 0, " ")                  # idx

        # 입력한 데이터로 서버에 request요청
        inst_xaquery_t1452.Request(0)
        print("이거 존재하니? : ", inst_xaquery_t1452)
        # 응답이 올 때까지 대기
        print("T1452 응답 대기 : ", XAQueryEventHandlerT1452.data_flag)
        result = XAConnector.watting(XAConnector, XAQueryEventHandlerT1452)
        print("T1452 응답 결과 : ", result)
        if result == TimeoutError:
            return TimeoutError

        # 원하는 데이터 받기
        count = 500
        stock_lists = []
        for i in range(count):
            hname = inst_xaquery_t1452.GetFieldData("t1452OutBlock1", "hname", i)    
            if hname == "" or hname == None:
                break
            price = inst_xaquery_t1452.GetFieldData("t1452OutBlock1", "price", i)    
            shcode = inst_xaquery_t1452.GetFieldData("t1452OutBlock1", "shcode", i)
            volume = inst_xaquery_t1452.GetFieldData("t1452OutBlock1", "volume", i)
            jnilvolume = inst_xaquery_t1452.GetFieldData("t1452OutBlock1", "jnilvolume", i)
            stock_list = {"hname": hname, "price": price, "shcode": shcode, "volume": volume, "jnilvolume": jnilvolume}
            stock_lists.append(stock_list)
            print("거래량 두개 구분 volume : ", volume, ", \tjnilvolume : ", jnilvolume)

        print("사용될 거래량 상위 데이터 : ", stock_lists)
        return stock_lists