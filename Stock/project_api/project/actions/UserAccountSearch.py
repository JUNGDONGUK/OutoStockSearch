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
from project.actions import UserConnectionManager

# 5-1 조회할 데이터가 있는 Res파일로 접근
class XAQueryEventHandlerT0424:
    
    def OnReceiveData(self, code):
        print("리시브 데이터 상태점검 : ", code)
        constants.DATAWAITING = True

class XAUserDataSelectEvent:
    # 5-2 해당 파일에서 데이터 조회
    def accountSelect(reqeust):
        XAConnector = UserConnectionManager.XAConnector()
        if XAConnector.is_connected() == False:
            try:
                XAConnector.connect_server()
                print("로그인할 유저아이디 : ", constants.LOGINID)
                XAConnector.login()
                print("로그인 중 문제?")
                reqeust.session['user_id'] = user_id
                reqeust.session['accounts'] = XAConnector.get_account_list()
            except:
                print("로그인 처리 중 에러가 발생하였습니다.")
                return HttpResponse(json.dumps({'status' : 'FAIL'}))

        # 5-2-1
        # 서버로 부터 계좌번호, 비밀번호 받기
        responseData = {}
        accountNum = reqeust.POST.get("accountNum").strip()
        accountPw = reqeust.POST.get("accountPw").strip()
        accountNum = reqeust.POST.get("accountNum").strip()
        accountPw = reqeust.POST.get("accountPw").strip()
        print("데이터 검증 : ", accountNum, " & ", accountPw)

        # 5-2-2
        # 쿼리핸들러를 이용해 DevCenter에 접근하기
        pythoncom.CoInitialize()
        instXAQueryT0424 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandlerT0424)
        pythoncom.CoUninitialize()

        # 5-2-3
        # 가져올 데이터가 들어있는 res파일 생성해주기
        instXAQueryT0424.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t0424.res"

        # 5-2-4
        # 서버에 request보낼 데이터 세팅하기
        # DevCenter1을 열어보면 InBlock에는 데이터를 넣어주어야하는 목록이 적혀있다. 여기에 데이터를 넣어줄 때는 SetFieldData를 쓴다.
        # 파라미터는 1. 블럭명, 2. 요소명, 3. 단일데이터인지 멀티데이터인지 구분(단일이면 0), 4. 집어넣을 값 
        instXAQueryT0424.SetFieldData("t0424InBlock", "accno", 0, accountNum) # 계좌정보
        instXAQueryT0424.SetFieldData("t0424InBlock", "passwd", 0, accountPw) # 비밀번호
        instXAQueryT0424.SetFieldData("t0424InBlock", "prcgb", 0, 1)          # 단가 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "chegb", 0, 0)          # 체결 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "dangb", 0, 0)          # 단일가 구분
        instXAQueryT0424.SetFieldData("t0424InBlock", "charge", 0, 1)         # 제비용 포함여부
        instXAQueryT0424.SetFieldData("t0424InBlock", "cts_expcode", 0, " ")  # CTS 종목번호

        # 5-2-5
        # 입력한 데이터로 서버에 request요청
        instXAQueryT0424.Request(0)

        # 5-2-6 
        # 응답이 올 때까지 대기
        while constants.DATAWAITING == False:
            pythoncom.PumpWaitingMessages()
        # 5-2-7
        # Response된 응답을 이용해 원하는 데이터 추출하기
        estimatedNetWorth = instXAQueryT0424.GetFieldData("t0424OutBlock", "sunamt", 0)                     # 추정 순자산
        totalPrice = instXAQueryT0424.GetFieldData("t0424OutBlock1", "mamt", 0)                             # 매입금액
        evaluationPNL = instXAQueryT0424.GetFieldData("t0424OutBlock1", "tdtsunik", 0)                      # 평가손익
        print('추정자산: ', estimatedNetWorth, '\n매입금액 : ', totalPrice, '\n평가손익 : ', evaluationPNL)

        evaluationRateOfReturnByStock = ""
        if estimatedNetWorth != None and estimatedNetWorth != "" and totalPrice != None and totalPrice != "" and  evaluationPNL != None and evaluationPNL != "":
            evaluationRateOfReturnByStock =  round((int(evaluationPNL) / int(totalPrice)), 1)                # 평가 수익율
            print('평가 수익율: ', evaluationRateOfReturnByStock)
            

        realProfit = instXAQueryT0424.GetFieldData("t0424OutBlock", "dtsunik", 0)                           # 실현손익
        print('실현손익: ', realProfit)

        realRateOfReturnByStock = ""
        if estimatedNetWorth != None and estimatedNetWorth != "" and realProfit != None and realProfit != "":
            realRateOfReturnByStock = round((int(realProfit) / (int(realProfit) + int(estimatedNetWorth))), 1)  # 실현 수익율
            print('실현 수익율: ', realRateOfReturnByStock)

        responseData = {
            'estimatedNetWorth' : estimatedNetWorth,
            'totalPrice' : totalPrice,
            'evaluationPNL' : evaluationPNL,
            'evaluationRateOfReturnByStock' : evaluationRateOfReturnByStock,
            'realProfit' : realProfit,
            'realRateOfReturnByStock' : realRateOfReturnByStock
        }

        constants.DATAWAITING = False
        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'data' : responseData}))




