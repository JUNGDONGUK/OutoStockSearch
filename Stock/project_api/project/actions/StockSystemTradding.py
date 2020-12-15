# 주식 종목 조회
from project import views
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
import win32com.client
import pythoncom
import time
from project.actions.UserConnectionManager import XAConnector
from core.constants import *
from datetime import datetime



# TODO
# 나중에는 화면에서 몇일 평균 거래량으로 평일 이동평균선을 돌파할 때 구매할 것인지를 받아서 입혀주는게 더 효율적일듯하다.

class XAStockSystemTraddingEvent:
    def stock_system_tradding(request):
        time.sleep(1)
        print('실행 : stock_system_tradding')
        # 클라이언트 단에서 값 가져오기
        algorism_type = request.POST.get("algorismType")
        sdate = request.POST.get("sdate")
        edate = request.POST.get("edate")
        
        # 데이터 검증
        if (algorism_type == "" or algorism_type == None):
            return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '차트를 불러오는 도중  발생하였습니다.', 'errorCode' : VALUEERROR}))
        
        # 사용할 주식 종목 모음        
        use_stock = []
        
        # 데이터 연속조회 여부 판단
        data_search_is_continue = False
        
        time.sleep(1)
        stock_lists = XAConnector.high_volume_stock_search(XAConnector)

        # 알고리즘 종류에 부합하는 형태로 데이터 불러오기
        if algorism_type == SHORTTERM:
            
            # 전체 종목 중 거래량이 터진 종목 조회
            for stock_list in stock_lists:
                time.sleep(0.5)  # TR 횟수 제한때문에...
                stock_data_lists = XAConnector.stock_chart(XAConnector, stock_list['shcode'], 2, 1, 60, sdate, edate, data_search_is_continue)
                data_search_is_continue = True

                # 해당 종목의 60일간 평균 거래량 조회
                stock_vol = 0
                average_of_stock_vol = 0
                for stock_data_list in stock_data_lists: # 아 지금 stock_data_lists이걸 참조할 때마다 계속 데이터를 서버에 요청하고 있는데 이걸 막아야해
                    stock_vol = stock_vol + int(stock_data_list['volume'])
                if stock_vol != 0:
                    average_of_stock_vol = float(stock_vol/ len(stock_data_lists))

                # 오늘이 60일 평균 거래량보다 5배 많은 날인 경우인 주식들만 리스트에 담아줌
                if float(stock_data_lists[len(stock_data_lists)-1]['volume']) > (average_of_stock_vol * 5) :
                    # 5일 이동평균선 조회
                    sum_of_stock_close = 0
                
                    for i in range(5):
                        sum_of_stock_close = sum_of_stock_close + float(stock_data_lists[len(stock_data_lists)-1-i]['price'])
                    average_of_stock_close = float(sum_of_stock_close / 5)
                    
                    # 5이평을 넘어선 종목 조회 후 사용할 종목으로 지정해주기
                    if float(stock_data_lists[len(stock_data_lists)-1]['price']) > average_of_stock_close :
                        use_stock.append(stock_list)
                    else :
                        pass
                else :
                    pass

        elif algorism_type == LONGTERM: 

            # 전체 종목 중 거래량이 터진 종목 조회
            for stock_list in stock_lists:
                time.sleep(0.5)  # TR 횟수 제한때문에...
                stock_data_lists = XAConnector.stock_chart(XAConnector, stock_list['shcode'], 2, 1, 60, sdate, edate, data_search_is_continue)
                data_search_is_continue = True

                # 해당 종목의 150일간 평균 거래량 조회
                stock_vol = 0
                for stock_data_list in stock_data_lists:
                    stock_vol = stock_vol + int(stock_data_list['volume'])
                average_of_stock_vol = float(stock_vol/ len(stock_data_lists))

                # 오늘이 150일 평균 거래량보다 2.5배 많은 날인 경우인 주식들만 리스트에 담아줌
                if float(stock_data_lists[len(stock_data_lists)-1]['volume']) > (average_of_stock_vol * 2.5) :
                    
                    # 30일 이동평균선 조회
                    sum_of_stock_close = 0
                    for i in range(30):
                        sum_of_stock_close = sum_of_stock_close + float(stock_data_lists[len(stock_data_lists)-1-i]['price'])
                    average_of_stock_close = float(sum_of_stock_close / 30)

                    # 30이평을 넘어선 종목 조회 후 사용할 종목으로 지정해주기
                    if float(stock_data_lists[len(stock_data_lists)-1]['price']) > average_of_stock_close :
                        use_stock.append(stock_list)

        print('시스템 트레이딩할 종목 조회 성공')

        return HttpResponse(json.dumps({'status' : 'SUCCESS', 'use_stock': use_stock}))
