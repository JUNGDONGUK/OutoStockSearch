# 종목 검색
class XAQueryEventHandlerT8430:
    data_flag = False
    def OnReceiveData(self, code):
        print("리시브 데이터 상태점검 : ", code)
        XAQueryEventHandlerT8430.data_flag = True