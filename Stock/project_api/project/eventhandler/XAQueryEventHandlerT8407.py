# 주식멀티 현재가 조회(이걸로는 현재가만 조회)
class XAQueryEventHandlerT8407:
    data_flag = False
    def OnReceiveData(self, code):
        print("T8407 데이터 상태점검 : ", code)
        XAQueryEventHandlerT8407.data_flag = True