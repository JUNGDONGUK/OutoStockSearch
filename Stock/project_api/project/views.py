import win32com.client
import pythoncom
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from core import constants
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json   #json 파일 형식 import
from project.actions.UserConnectionManager import XAConnector

# 1. MainPage 접속
def main(request): 
    # 여기서 request는 무조건 들어오게 되어있다 왜? 요청에 대한 응답을 보내주는 부분이기 때문에 요청은 반드시 1개 이상 들어와야 정상이다.

    # 로그인 유무 판단 부분    
    if (XAConnector.is_connected(XAConnector) == True):
        if XAConnector.account_list != None:
            return HttpResponseRedirect(constants.MAINPAGE)
        else :
            loginCheck(request)
    else :
        return loginCheck(request)


# 2. 로그인한 유저가 아닐 시 loginPage로 이동
def loginCheck(request):
    return HttpResponseRedirect(constants.LOGINPAGE)




