# 종목 검색
class XAQueryEventHandlerCSPAT00600:
    data_flag = False
    def OnReceiveData(self, code):
        print("CSPAT00600 데이터 상태점검 : ", code)
        XAQueryEventHandlerCSPAT00600.data_flag = True