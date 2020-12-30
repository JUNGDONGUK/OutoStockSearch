# 계좌 정보 조회
class XAQueryEventHandlerT1452:
    data_flag = False
    def OnReceiveData(self, code):
        print("T1452 데이터 상태점검 : ", code)
        XAQueryEventHandlerT1452.data_flag = True