# 계좌 정보 조회
class XAQueryEventHandlerT0424:
    data_flag = False
    def OnReceiveData(self, code):
        print("T0424 데이터 상태점검 : ", code)
        XAQueryEventHandlerT0424.data_flag = True