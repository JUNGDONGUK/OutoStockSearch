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
import datetime
from django.http import HttpResponseRedirect, HttpResponse
from urllib.request import urlopen
from bs4 import BeautifulSoup


from project.eventhandler.XASessionEventHandler import XASessionEventHandler
from project.eventhandler.XAQueryEventHandlerT0424 import XAQueryEventHandlerT0424
from project.eventhandler.XAQueryEventHandlerT1452 import XAQueryEventHandlerT1452
from project.eventhandler.XAQueryEventHandlerT4201 import XAQueryEventHandlerT4201
from project.eventhandler.XAQueryEventHandlerT8407 import XAQueryEventHandlerT8407
from project.eventhandler.XAQueryEventHandlerT8430 import XAQueryEventHandlerT8430
from project.eventhandler.XAQueryEventHandlerCSPAT00600 import XAQueryEventHandlerCSPAT00600
from project.eventhandler.XAQueryEventHandlerCSPAQ13700 import XAQueryEventHandlerCSPAQ13700

xa_session = None
first_search = True
kospi = None
is_first_check = True
finance_crawling_list = None
tune_data_list = None
tune_t4201 = []
# ebest_user_id = None
# ebest_user_accounts = None
# ebest_user_pw = ""
# ebest_user_cert_pw = ""
#  ==============================================================================================
# 서버연결

def connect_server():
    global xa_session
    print("\n\n서버연결 시도합니다. xa_session: ", xa_session,  "is_connected: ", is_connected(), "\n\n")
    print("접속상태 확인 : ", xa_session)
    pythoncom.CoInitialize()
    xa_session = win_client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)
    pythoncom.CoUninitialize()
    
    return xa_session.ConnectServer(DEMO_SERVER, SERVER_PORT)

def is_connected():
    global xa_session
    if xa_session is None:
        result = False
    else:
        result = xa_session.IsConnected()
        return result

def disconnect_server():
    global xa_session
    global first_search
    global kospi
    try:
        if xa_session != None:
            xa_session.DisconnectServer()
            xa_session = None
            first_search = True
            kospi = None    
        else:
            xa_session = None
            first_search = True
            kospi = None    
    except Exception as e:
        print(e)
        return False
    return True



#  ==========================================================================================
# 데이터 수신 대기



def waiting(handler):
        print("\n\n ", handler, " 정보를 받아오는 중입니다.\n\n")
        while handler.data_flag == False:
            pythoncom.PumpWaitingMessages()
            # end = time.time()
            # now_time = end - start
            # if (now_time) >= 30:
            #     return TimeoutError
        return data_flag_tune(handler)

def data_flag_tune(handler):
    handler.data_flag = False
    return True



#  ==============================================================================================
# 로그인

# 기존 로그인 메서드
# def do_login(request):
#     print("\n\n로그인 시작합니다.\n\n")
#     global xa_session
#     global kospi
#     print("접속상태 확인 : ", xa_session)
#     ebest_user_id = request.session.get("ebest_user_id", None)
#     ebest_user_pw = request.session.get("ebest_user_pw", "")
#     ebest_user_cert_pw = request.session.get("ebest_user_cert_pw", "")
#     ebest_user_accounts = request.session.get("ebest_user_accounts", None)
#     # try:
#     # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
#     if xa_session != None:
#         print("연결 되어 있습니다.")
#         login(ebest_user_id, ebest_user_pw, ebest_user_cert_pw)
#         data = {
#             "user_id" : ebest_user_id,
#             "accounts" : ebest_user_accounts
#         }
#         return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data}))
#     else :
#         print("연결 되어 있지 않습니다. 연결을 시도합니다.")
#         connect_server()
#     if request.method == "POST":
#         user_id = request.POST.get("userId")
#         user_pw = request.POST.get("userPw")
#         cert_pw = request.POST.get("userCertPassword")
#     login(user_id, user_pw, cert_pw)
#     account_list = get_account_list()

#     request.session["ebest_user_id"] = user_id
#     request.session["ebest_user_pw"] = user_pw
#     request.session["ebest_user_cert_pw"] = cert_pw
#     request.session["ebest_user_accounts"] = account_list

#     ebest_user_id = user_id
#     ebest_user_accounts = account_list

#     data = {
#         "user_id" : ebest_user_id,
#         "accounts" : ebest_user_accounts
#     }
#     # HttpResponse.set_cookie("accessCookie", data)

#     print("로그인 된 서버명 : ", xa_session.GetServerName())
#     kospi = stock_item(request)
#     return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data}))




# 튜닝할 로그인 메서드(위 메서드가 기존 메서드)
def do_login(request):
    print("\n\n로그인 시작합니다.\n\n")
    global xa_session
    global kospi
    print("접속상태 확인 : ", xa_session)
    ebest_user_id = request.session.get("ebest_user_id", None)
    ebest_user_pw = request.session.get("ebest_user_pw", "")
    ebest_user_cert_pw = request.session.get("ebest_user_cert_pw", "")
    ebest_user_accounts = request.session.get("ebest_user_accounts", None)
    # try:
    # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
    if xa_session != None:
        print("연결 되어 있습니다.")
        login(ebest_user_id, ebest_user_pw, ebest_user_cert_pw)
        data = {
            "user_id" : ebest_user_id,
            "accounts" : ebest_user_accounts
        }
        return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data}))
    else :
        print("연결 되어 있지 않습니다. 연결을 시도합니다.")
        connect_server()
    if request.method == "POST":
        user_id = request.POST.get("userId")
        user_pw = request.POST.get("userPw")
        cert_pw = request.POST.get("userCertPassword")
    
    result = login(user_id, user_pw, cert_pw)
    if result == ValueError or result == TimeoutError :
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "로그인 중 문제가 발생하였습니다."}))


    account_list = get_account_list()

    request.session["ebest_user_id"] = user_id
    request.session["ebest_user_pw"] = user_pw
    request.session["ebest_user_cert_pw"] = cert_pw
    request.session["ebest_user_accounts"] = account_list

    ebest_user_id = user_id
    ebest_user_accounts = account_list

    data = {
        "user_id" : ebest_user_id,
        "accounts" : ebest_user_accounts
    }
    # HttpResponse.set_cookie("accessCookie", data)

    print("로그인 된 서버명 : ", xa_session.GetServerName())
    kospi = stock_item(request)
    print("코스피 데이터 조회 완료")
    finance_crawling(request)
    print("finance Crawling 완료")
    return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data}))


def do_logout(request):
    print("\n\n로그아웃 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    if disconnect_server():
        return HttpResponse(json.dumps({"status" : "SUCCESS"}))
    else:
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "로그아웃 중 문제가 발생하였습니다."}))


def login(user_id, user_pw, user_cpwd):
    global xa_session
    print("접속상태 확인 : ", xa_session)
    ebest_id = user_id
    ebest_pw = user_pw
    ebest_cpwd = user_cpwd
    if ebest_id == None or ebest_pw == None: 
        return ValueError
    else: 
        session_connect = xa_session.Login(ebest_id, ebest_pw, ebest_cpwd, 0, 0)
        XASessionEventHandler.login_flag = False
        print(session_connect)
        if session_connect != True :
            return ValueError

    # 응답이 올 때까지 대기
    print("XASession 응답 대기 : ", XASessionEventHandler.data_flag)
    result = waiting(XASessionEventHandler)
    print("XASession 응답 결과 : ", result)
    if result == TimeoutError:
        return TimeoutError


    return XASessionEventHandler.login_flag



#  ==================================================================================
# 계좌 정보 조회


def account_select(request):
    print("\n\n유저정보 조회합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    # 서버로 부터 계좌번호, 비밀번호 받기
    response_data = {}
    account_num = request.POST.get("accountNum").strip()
    account_pw = request.POST.get("accountPw").strip()
    if (account_num == "" or account_num == None) :
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "계좌정보가 존재하지 않습니다. 로그인페이지로 이동합니다.", "errorCode" : VALUEERROR}))

    is_continue = False
    response_data = user_data_search(account_num, account_pw, is_continue)
    is_continue = True
    if (response_data == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    elif (response_data == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))

    return HttpResponse(json.dumps({"status" : "SUCCESS", "userProperty" : response_data[0], "transactionDetails": response_data[1]}))


def get_account_list():
    global xa_session
    account_ctn = xa_session.GetAccountListCount()
    account_list = []
    for i in range(account_ctn):
        account_num = xa_session.GetAccountList(i)
        account_list.append(account_num)
    
    return account_list

def user_data_search(account_num, account_pw, is_continue):
    print("접속상태 확인 : ", xa_session)
    if is_connected() == None:
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
    result = waiting(XAQueryEventHandlerT0424)
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
            "expcode": expcode,
            "hname": hname,
            "price": price,
            "mdposqt": mdposqt,
            "sunikrt": sunikrt
        }
        retained_item_list.append(retained_item)
    
    print("유저 보유종목은? : ", retained_item_list)
    return [user_property, retained_item_list]




#  =====================================================================================
# 주식 종목 조회

def stock_item(request):
    print("\n\n주식 종목 조회합니다.\n\n")
    global xa_session
    global first_search
    print("접속상태 확인 : ", xa_session)
    # print(xa_session.ConnectTimeOut(3000))
    
    if first_search:
        stock_category = 1
        stock_name = ""
        print("최초 코시피 조회합니다.")
    # 서버로 부터 종목 유형(코스피, 코스닥 or 전체), 종목 이름 받기
    else :
        stock_category = request.POST.get("stockCategory").strip()
        stock_name = request.POST.get("stockName").strip()

    print("\n외부에서 들어온 데이터 목록\n  =>stock_category : ", stock_category, "\n  =>stock_name : ", stock_name)
    

    # 데이터 검증
    if (stock_category == "" or stock_name == None):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "해당 종목은 존재하지 않습니다.", "errorCode" : VALUEERROR}))
        
    is_continue = False
    response_data = stock_item_search(stock_category, is_continue)
    is_continue = True

    # 받은 데이터 가공하기
    if (response_data == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "ConnectionRefusedError", "errorCode" : SESSIONOUT}))
    elif (response_data == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "TimeoutError", "errorCode" : SESSIONOUT}))

    # 유저가 원하는 데이터만 따로 세팅
    data = []
    for stock_list in response_data:
        if stock_name in stock_list["hname"]:
            data.append(stock_list)
        else:
            continue

    if first_search:
        first_search = False
        return data
    else :
        return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data}))


def stock_item_search(stock_category, is_continue):

    # 쿼리핸들러를 이용해 DevCenter에 접근하기
    pythoncom.CoInitialize()
    inst_xaquery_t8430 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT8430)
    pythoncom.CoUninitialize()

    # 가져올 데이터가 들어있는 res파일 생성해주기
    inst_xaquery_t8430.ResFileName = "C:\\eBEST\\xingAPI\\debug\\xingAPI_Program_Debug(2020.10.08)\\Res\\t8430.res"
    # 서버에 request보낼 데이터 세팅하기
    inst_xaquery_t8430.SetFieldData("t8430InBlock", "gubun", 0, stock_category) # 주식 카테고리 선택(0 : 전체, 1: 코스피, 2: 코스닥)
    
    # 입력한 데이터로 서버에 request요청
    print("\n\nrequest직전!")
    print("IsConnected : ", xa_session.IsConnected())
    print("GetAccountListCount : ", xa_session.GetAccountListCount())
    print("IsLoadAPI : ", xa_session.IsLoadAPI())
    print("GetServerName : ", xa_session.GetServerName())
    errorCode = xa_session.GetLastError()
    print("GetLastError : ", errorCode)
    print("GetErrorMessage : ", xa_session.GetErrorMessage(errorCode))
    
    req_number = inst_xaquery_t8430.Request(is_continue)
    print("\n\ndll 요청 성공 유무? : ", req_number)
    
    print("T8430 응답 대기 : ", XAQueryEventHandlerT8430.data_flag)
    result = waiting(XAQueryEventHandlerT8430)
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
        stock = {"hname" : hname, "shcode" : shcode, "recprice" : recprice, "uplmtprice" : uplmtprice, "dnlmtprice" : dnlmtprice}
        # expcode = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "expcode", 0)   # 확장코드
        # etfgubun = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "etfgubun", 0)   # ETF구분
        # jnilclose = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "jnilclose", 0)   # 전일가
        # memedan = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "memedan", 0)   # 주문수량단위
        stock_list.append(stock)

    print("종목 조회 완료되었습니다. =========================================================")
    XAQueryEventHandlerT8430.data_flag = False
    return stock_list


# 거래량 상위 100개 조회
def high_volume_stock_search():
    # TODO Print 지우기
    print("접속상태 확인 : ", xa_session)
    if is_connected() == None:
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
    result = waiting(XAQueryEventHandlerT1452)
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


#  ==================================================================================
# 차트 정보 조회

def stock_chart(request):
    print("\n\n차트 정보 조회합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    # 클라이언트 단에서 값 가져오기
    shcode = request.POST.get("shcode")
    gubun = request.POST.get("gubun")
    ncnt = request.POST.get("ncnt")
    qrycnt = request.POST.get("qrycnt")
    sdate = request.POST.get("sdate")
    edate = request.POST.get("edate")
    acnt_no = request.POST.get("AcntNo")
    input_pw = request.POST.get("AccountPw")

    # 데이터 검증
    if (shcode == "" or shcode == None):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "stock_chart에서 차트를 불러오는 도중  발생하였습니다.", "errorCode" : VALUEERROR}))
    
    # 데이터 연속조회 여부 판단
    chart_is_continue = False
    account_is_continue = False

    # dll파일을 통해 데이터 받기
    data = stock_chart_search(shcode, gubun, ncnt, qrycnt, sdate, edate, chart_is_continue)
    if (data == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    elif (data == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))

    
    # 거래 내역 조회하기
    datas = user_data_search(acnt_no, input_pw, account_is_continue)
    if (datas == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    elif (datas == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    print("거래내역조회 성공")

    return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data, "userProperty" : datas[0], "transactionDetails": datas[1]}))


def stock_chart_search(shcode, gubun, ncnt, qrycnt, sdate, edate, is_continue):
    # TODO Print 지우기
    if is_connected() == None:
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
        result = waiting(XAQueryEventHandlerT4201)
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
        result = waiting(XAQueryEventHandlerT4201)
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
        
        stock_detail = {"stock_date" : stock_date[0:4] + "-" + stock_date[4:6] + "-" + stock_date[6:8], "stock_time" : stock_time, "stock_low" : stock_low, "stock_open" : stock_open, "stock_close" : stock_close, "stock_high" : stock_high, "stock_jdiff_vol" : stock_jdiff_vol}
        stock_detail_list.append(stock_detail)


    return stock_detail_list



#  =================================================================================
# 주식 거래
def stock_system_tradding(request):
    global kospi
    print("\n\n 시스템트레이딩 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    # 클라이언트 단에서 값 가져오기
    algorism_type = request.POST.get('algorismType')
    sdate = request.POST.get('sdate')
    edate = request.POST.get('edate')
    print("조회 일자 : ", sdate, " ~ ", edate)
    
    # 데이터 검증
    if (algorism_type == "" or algorism_type == None):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "차트를 불러오는 도중  발생하였습니다.", "errorCode" : VALUEERROR}))
    
    # 사용할 주식 종목 모음        
    use_stock = []
    
    # 데이터 연속조회 여부 판단
    data_search_is_continue = False
    
    stock_lists = kospi

    # 알고리즘 종류에 부합하는 형태로 데이터 불러오기
    if algorism_type == SHORTTERM:
        
        # 전체 종목 중 거래량이 터진 종목 조회
        for stock_list in stock_lists:
            time.sleep(0.5)  # TR 횟수 제한때문에...
            stock_data_lists = stock_chart_search(stock_list["shcode"], 2, 1, 60, sdate, edate, data_search_is_continue)
            data_search_is_continue = True

            # 해당 종목의 60일간 평균 거래량 조회
            stock_vol = 0
            average_of_stock_vol = 0
            for stock_data_list in stock_data_lists: # 아 지금 stock_data_lists이걸 참조할 때마다 계속 데이터를 서버에 요청하고 있는데 이걸 막아야해
                stock_vol = stock_vol + int(stock_data_list["volume"])
            if stock_vol != 0:
                average_of_stock_vol = float(stock_vol/ len(stock_data_lists))

            # 오늘이 60일 평균 거래량보다 5배 많은 날인 경우인 주식들만 리스트에 담아줌
            if float(stock_data_lists[len(stock_data_lists)-1]["volume"]) > (average_of_stock_vol * 5) :
                # 5일 이동평균선 조회
                sum_of_stock_close = 0
            
                for i in range(5):
                    sum_of_stock_close = sum_of_stock_close + float(stock_data_lists[len(stock_data_lists)-1-i]["price"])
                average_of_stock_close = float(sum_of_stock_close / 5)
                
                # 5이평을 넘어선 종목 조회 후 사용할 종목으로 지정해주기
                if float(stock_data_lists[len(stock_data_lists)-1]["price"]) > average_of_stock_close :
                    use_stock.append(stock_list)
                else :
                    pass
            else :
                pass

    elif algorism_type == LONGTERM: 

        # 전체 종목 중 거래량이 터진 종목 조회
        for stock_list in stock_lists:
            time.sleep(0.5)  # TR 횟수 제한때문에...
            stock_data_lists = stock_chart_search(stock_list["shcode"], 2, 1, 60, sdate, edate, data_search_is_continue)
            data_search_is_continue = True

            # 해당 종목의 150일간 평균 거래량 조회
            stock_vol = 0
            for stock_data_list in stock_data_lists:
                stock_vol = stock_vol + int(stock_data_list["volume"])
            average_of_stock_vol = float(stock_vol/ len(stock_data_lists))

            # 오늘이 150일 평균 거래량보다 2.5배 많은 날인 경우인 주식들만 리스트에 담아줌
            if float(stock_data_lists[len(stock_data_lists)-1]["volume"]) > (average_of_stock_vol * 2.5) :
                
                # 30일 이동평균선 조회
                sum_of_stock_close = 0
                for i in range(30):
                    sum_of_stock_close = sum_of_stock_close + float(stock_data_lists[len(stock_data_lists)-1-i]["price"])
                average_of_stock_close = float(sum_of_stock_close / 30)

                # 30이평을 넘어선 종목 조회 후 사용할 종목으로 지정해주기
                if float(stock_data_lists[len(stock_data_lists)-1]["price"]) > average_of_stock_close :
                    use_stock.append(stock_list)

    print("시스템 트레이딩할 종목 조회 성공")

    return HttpResponse(json.dumps({"status" : "SUCCESS", "use_stock": use_stock}))


def stock_tradding(request):
    print("\n\n시스템 거래 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
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
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "do_stock_tradding에서 차트를 불러오는 도중  발생하였습니다.", "errorCode" : VALUEERROR}))
    
    # dll파일을 통해 데이터 받기
    data = do_stock_tradding(acnt_no, input_pw, isu_no, ord_qty, prd_prc, bns_tp_code, ordprc_ptn_code)
    if (data == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    elif (data == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))

    print("매매는 성공")

    # 거래 내역 조회하기
    account_is_continue = False
    transaction_details = user_data_search(acnt_no, input_pw, account_is_continue)
    if (transaction_details == ConnectionRefusedError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    elif (transaction_details == TimeoutError):
        return HttpResponse(json.dumps({"status" : "FAIL", "error" : "세션이 만료되었습니다.", "errorCode" : SESSIONOUT}))
    print("거래내역조회 성공")

    return HttpResponse(json.dumps({"status" : "SUCCESS", "data" : data, "userProperty" : transaction_details[0], "transactionDetails": transaction_details[1]}))


def do_stock_tradding(acnt_no, input_pw, isu_no, ord_qty, ord_prc, bns_tp_code, ordprc_ptn_code):
    # TODO Print 지우기
    if is_connected() == None:
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
    inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "MgntrnCode", 0, "000")
    inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "LoanDt", 0, "")
    inst_xaquery_cspat00600.SetFieldData("CSPAT00600InBlock1", "OrdCndiTpCode", 0, "0")
    
    # 입력한 데이터로 서버에 request요청
    inst_xaquery_cspat00600.Request(0)

    # 응답이 올 때까지 대기
    print("CSPAT00600 응답 대기 : ", XAQueryEventHandlerCSPAT00600.data_flag)
    result = waiting(XAQueryEventHandlerCSPAT00600)
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
    data = {"MbrNo": mbr_no, "AcntNo": acnt_no, "IsuNo": isu_no, "OrdPrc": ord_prc, "OrdQty": ord_qty, "BnsTpCode": bns_tp_code}
    return data


def stockTraddingState(acnt_no, input_pw, isu_no, ord_dt):
    # TODO Print 지우기
    if is_connected() == None:
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
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "IsuNo", 0, "A"+isu_no)     # 종목번호 => A는 주식을 의미
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "ExecYn", 0, 0)            # 체결여부
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "OrdDt", 0, ord_dt)         # 주문일 
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "SrtOrdNo2", 0, 000000000) # 시작주문번호 : 정순
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "BkseqTpCode", 0, 1)       # 역순구분 : 정순
    inst_xaquery_cspaq13700.SetFieldData("CSPAQ13700InBlock1", "OrdPtnCode", 0, 00)       # 주문유형코드
    
    # 입력한 데이터로 서버에 request요청
    inst_xaquery_cspaq13700.Request(0)

    # 응답이 올 때까지 대기
    print("CSPAQ13700 응답 대기 : ", XAQueryEventHandlerCSPAQ13700.data_flag)
    result = waiting(XAQueryEventHandlerCSPAQ13700)
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
        if stock_ord_qty == "":
            stock_ord_qty = 0
        if stock_exec_qty == "":
            stock_exec_qty = 0
        stock_non_exec_qty = int(stock_ord_qty) - int(stock_exec_qty)                                      # 미체결량
        data = {"stockBnsTpNm": stock_bns_tp_nm, "stockOrdQty": stock_ord_qty, "stockOrdPrc": stock_ord_prc, "stockExecQty": stock_exec_qty, "stockExecPrc": stock_exec_prc, "stockNonExecQty": stock_non_exec_qty}
        tradding_list.append(data)
    
    return tradding_list



#  ===========================================================================
# 데이터 크롤링
def finance_crawling(request):
    global finance_crawling_list
    global tune_data_list
    global is_first_check
    print("\n\웹 크롤링 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    html = urlopen("https://finance.naver.com/sise/sise_quant.nhn")  
    stock_html = BeautifulSoup(html, "html.parser") 

    finance_crawling_list = []
    titles = stock_html.find_all("a", attrs={"class":"tltle"})
    tds = stock_html.find_all("td", attrs={"class":"number"})
    count = 1
    for title in titles:
        crawling_data = {"no": count, "종목명": title.text, "종목코드": title["href"].split("=")[1].strip(), "현재가": "", "전일대비": "", "등락률": "", "거래량": "", "거래대금": "", "매수호가": "", "매도호가": "", "시가총액": "", "PER": "", "ROE": ""}
        value_list = ["현재가", "전일대비", "등락률", "거래량", "거래대금", "매수호가", "매도호가", "시가총액", "PER", "ROE"]
        for i in range(10):
            value = value_list.pop(0)
            tdVal = tds.pop(0).text
            crawling_data[value] = tdVal.strip().replace("\n", "").replace("\t", "").replace(" ", "")
        finance_crawling_list.append(crawling_data)
        count = count + 1
    
    if is_first_check :
        tune_data_list = tunning_data(finance_crawling_list)
        is_first_check = False
        return True
    else :
        return HttpResponse(json.dumps({"status": "SUCCESS", "crawlingList": finance_crawling_list, "tuneDataList": tune_data_list, "tuneT4201": tune_t4201}))

def tunning_data(crawling_list):
    global kospi
    global tune_t4201
    print("\n\n데이터 튜닝 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)

    tunning_lists = []
    compare_lists = []
    result_lists = []
    for kospi_data in kospi:
        for crawling_list_data in crawling_list:
            if kospi_data["hname"] == crawling_list_data["종목명"]:
                tunning_lists.append(kospi_data)
                compare_lists.append(crawling_list_data)
    system_datas = stock_system_tunning(tunning_lists)
    for crawling_list_data in compare_lists:
        for system_data in system_datas:
            if crawling_list_data["종목명"] == system_data["hname"]:
                per = crawling_list_data["PER"].replace(",", "").replace(" ", "")
                if per != "N/A":
                    if (float(per) < 6): 
                        result_lists.append(crawling_list_data)
                        tune_t4201.append(system_data)
                        # if len(t4201) <= len(crawling_list_data):

    return result_lists


def stock_system_tunning(tunning_lists):
    print("\n\n 시스템트레이딩 시작합니다.\n\n")
    print("접속상태 확인 : ", xa_session)
    # 클라이언트 단에서 값 가져오기
    algorism_type = SHORTTERM
    days_ago = datetime.datetime.now() - datetime.timedelta(days=60)
    sdate = days_ago.strftime("%Y%m%d")
    now_date = datetime.datetime.now()
    edate = now_date.strftime("%Y%m%d")
    
    # 사용할 주식 종목 모음        
    use_stock = []
    
    # 데이터 연속조회 여부 판단
    data_search_is_continue = False
    
    # 알고리즘 종류에 부합하는 형태로 데이터 불러오기
    if algorism_type == SHORTTERM:
        
        # 전체 종목 중 거래량이 터진 종목 조회
        for stock_list in tunning_lists:
            time.sleep(1)  # TR 횟수 제한때문에...

            # print("조회 일자 : ", sdate, " ~ ", edate)
            stock_data_lists = stock_chart_search(stock_list["shcode"], 2, 1, 60, sdate, edate, data_search_is_continue)

            # 해당 종목의 60일간 평균 거래량 조회
            stock_vol = 0
            average_of_stock_vol = 0

            if len(stock_data_lists) > 0:
                for stock_data_list in stock_data_lists: 
                    stock_vol = stock_vol + int(stock_data_list["stock_jdiff_vol"])
                if stock_vol != 0:
                    average_of_stock_vol = float(stock_vol/ len(stock_data_lists))

                # 오늘이 60일 평균 거래량보다 5배 많은 날인 경우인 주식들만 리스트에 담아줌
                if float(stock_data_lists[len(stock_data_lists)-2]["stock_jdiff_vol"]) > (average_of_stock_vol * 2) :
                    # 5일 이동평균선 조회
                    sum_of_stock_close = 0
                
                    for i in range(5):
                        sum_of_stock_close = sum_of_stock_close + float(stock_data_lists[len(stock_data_lists)-2-i]["stock_close"])
                    average_of_stock_close = float(sum_of_stock_close / 5)
                    
                    # 5이평을 넘어선 종목 조회 후 사용할 종목으로 지정해주기
                    if float(stock_data_lists[len(stock_data_lists)-2]["stock_close"]) > average_of_stock_close :
                        use_stock.append(stock_list)
                    else :
                        pass
                else :
                    pass
            else :
                print("데이터가 없습니다. stock_data_lists : ", stock_data_lists)
                pass

    print("시스템 트레이딩할 종목 조회 성공")

    return use_stock

def crawlingStockDetail(request):
    global tune_t4201
    key = request.POST.get("key")
    number = request.POST.get("number")
    if key == "tune":
        return HttpResponse(json.dumps({"status": "SUCCESS", "tuneT4201": tune_t4201[number]}))
    elif key == "origin":
        return tune_t4201[number]