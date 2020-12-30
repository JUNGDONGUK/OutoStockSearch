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
ebest_user_id = None
ebest_user_accounts = None
ebest_user_pw = ""
ebest_user_cert_pw = ""

def do_login(request):
    print("\n\n로그인 시작합니다.\n\n")
    global xa_session
    global ebest_user_id
    global ebest_user_accounts
    global ebest_user_pw
    global ebest_user_cert_pw
    # try:
    # 클라이언트단에서 값 받아 접속할 ID PW, 를 지정하기
    if xa_session != None:
        print('연결 되어 있습니다.')
        login(ebest_user_id, ebest_user_pw, ebest_user_cert_pw)
        data = {
            'user_id' : ebest_user_id,
            'accounts' : ebest_user_accounts
        }
        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))
    else :
        print('연결 되어 있지 않습니다. 연결을 시도합니다.')
        connect_server()
    if request.method == 'POST':
        user_id = request.POST.get("userId")
        user_pw = request.POST.get("userPw")
        cert_pw = request.POST.get("userCertPassword")
    login(user_id, user_pw, cert_pw)
    account_list = get_account_list()

    ebest_user_id = user_id
    ebest_user_pw = user_pw
    ebest_user_cert_pw = cert_pw
    ebest_user_accounts = account_list

    data = {
        'user_id' : ebest_user_id,
        'accounts' : ebest_user_accounts
    }
    # HttpResponse.set_cookie('accessCookie', data)

    print('\n\n', '로그인 완료 : ', data, '\n\n')

    stockList = stock_item(request)

    print('\n\n', '주식 목록 조회 완료 : ', stockList, '\n\n')
    
    stockList = stock_item(request)

    print('\n\n', '주식 목록 조회 완료 : ', stockList, '\n\n')

    return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : data}))

    # except :
    #     return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '유저 정보를 가져오는 도중  발생하였습니다.'}))



def login(user_id, user_pw, user_cpwd):
    global xa_session
    ebest_id = user_id
    ebest_pw = user_pw
    ebest_cpwd = user_cpwd
    if ebest_id == None or ebest_pw == None: 
        return ValueError
    else: 
        xa_session.Login(ebest_id, ebest_pw, ebest_cpwd, 0, 0)
    
    # 응답이 올 때까지 대기
    print("XASession 응답 대기 : ", XASessionEventHandler.data_flag)
    result = waiting(XASessionEventHandler)
    print("XASession 응답 결과 : ", result)
    if result == TimeoutError:
        return TimeoutError

    XASessionEventHandler.login_flag = False

    return XASessionEventHandler.login_flag




def connect_server():
    global xa_session
    print('서버연결 시도합니다.\n     xa_session: ', xa_session,  'is_connected: ', is_connected())
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
    try:
        xa_session = None
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
            time.sleep(0.001)
            # end = time.time()
            # now_time = end - start
            # if (now_time) >= 30:
            #     return TimeoutError
        return data_flag_tune(handler)

def data_flag_tune(handler):
    handler.data_flag = False
    return True



def get_account_list():
    global xa_session
    account_ctn = xa_session.GetAccountListCount()
    account_list = []
    for i in range(account_ctn):
        account_num = xa_session.GetAccountList(i)
        account_list.append(account_num)
    
    return account_list





#  =====================================================================================
# 주식 종목 조회

def stock_item(request):
    print("\n\n주식 종목 조회합니다.\n\n")
    global xa_session
    print(xa_session)
    time.sleep(0.5)
    # 서버로 부터 종목 유형(코스피, 코스닥 or 전체), 종목 이름 받기
    stock_category = 0
    stock_name = ""
    print("\n외부에서 들어온 데이터 목록\n  =>stock_category : ", stock_category, "\n  =>stock_name : ", stock_name)
    

    # 데이터 검증
    if (stock_category == "" or stock_name == None):
        return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '해당 종목은 존재하지 않습니다.', 'errorCode' : VALUEERROR}))
        
    is_continue = False
    response_data = stock_item_search(stock_category, is_continue)
    is_continue = True

    # 받은 데이터 가공하기
    if (response_data == ConnectionRefusedError):
        return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'ConnectionRefusedError', 'errorCode' : SESSIONOUT}))
    elif (response_data == TimeoutError):
        return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : 'TimeoutError', 'errorCode' : SESSIONOUT}))

    # 유저가 원하는 데이터만 따로 세팅
    data = []
    print("response_data???? : ", response_data)
    for stock_list in response_data:
        if stock_name in stock_list['hname']:
            data.append(stock_list)
        else:
            continue

    return data


def stock_item_search(stock_category, is_continue):
    # 쿼리핸들러를 이용해 DevCenter에 접근하기
    pythoncom.CoInitialize()
    inst_xaquery_t8430 = win_client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT8430)
    pythoncom.CoUninitialize()

    # 가져올 데이터가 들어있는 res파일 생성해주기
    inst_xaquery_t8430.ResFileName = "C:\\eBEST\\xingAPI\\debug\\xingAPI_Program_Debug(2020.10.08)\\Res\\t8430.res"

    # 서버에 request보낼 데이터 세팅하기
    inst_xaquery_t8430.SetFieldData("t8430InBlock", "gubun", 0, 0) # 주식 카테고리 선택(0 : 전체, 1: 코스피, 2: 코스닥)
    
    # 입력한 데이터로 서버에 request요청
    req_number = inst_xaquery_t8430.Request(is_continue)

    # 응답이 올 때까지 대기
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
        stock = {'hname' : hname, 'shcode' : shcode, 'recprice' : recprice, 'uplmtprice' : uplmtprice, 'dnlmtprice' : dnlmtprice}
        # expcode = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "expcode", 0)   # 확장코드
        # etfgubun = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "etfgubun", 0)   # ETF구분
        # jnilclose = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "jnilclose", 0)   # 전일가
        # memedan = inst_xaquery_t8430.GetFieldData("t8430OutBlock", "memedan", 0)   # 주문수량단위
        stock_list.append(stock)

    print("종목 조회 완료되었습니다. =========================================================")
    return stock_list


# 거래량 상위 100개 조회
def high_volume_stock_search():
    time.sleep(1)
    # TODO Print 지우기
    print("high_volume_stock_search 접속상태 확인 : ", is_connected())
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
