# 종목 검색
class XAQueryEventHandlerT8430:
    data_flag = False
    def OnReceiveData(self, code):
        XAQueryEventHandlerT8430.data_flag = True