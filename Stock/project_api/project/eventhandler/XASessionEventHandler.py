from django.http import HttpResponseRedirect,HttpResponse

# 로그인이벤트 처리 클래스 구현
class XASessionEventHandler:
    data_flag = False
    def OnLogin(self, code, msg):
        if code == '0000':
            XASessionEventHandler.data_flag = True
            return code
        else :
            print('로그인 실패 : ', msg)
            return msg

    def OnDisconnect(self, code):
        print('OnDisconnect')

    def OnLogout(self):
        print('OnLogout')
