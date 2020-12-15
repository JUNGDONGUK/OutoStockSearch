# 종목 검색
class XAQueryEventHandlerCSPAQ13700:
    data_flag = False
    def OnReceiveData(self, code):
        print("CSPAQ13700 데이터 상태점검 : ", code)
        XAQueryEventHandlerCSPAQ13700.data_flag = True