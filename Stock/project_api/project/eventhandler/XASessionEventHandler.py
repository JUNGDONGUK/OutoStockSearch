from django.http import HttpResponseRedirect,HttpResponse

# 로그인이벤트 처리 클래스 구현
class XASessionEventHandler:
    login_flag = False
    def OnLogin(self, code, msg):
        if code == '0000':
            XASessionEventHandler.login_flag = True
        else :
            XASessionEventHandler.OnDisconnect(self, code, msg)

    def OnDisconnect(self, code, msg):
        XASessionEventHandler.login_flag = False
        return HttpResponse(json.dumps({'status' : 'FAIL', 'error' : '아이디 또는 패스워드를 확인하세요'}))

