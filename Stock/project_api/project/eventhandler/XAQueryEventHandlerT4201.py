# 주식차트 종합(년봉, 월봉, 주봉, 일봉 조회용(현재가는 T8407로 조회할 예정))
class XAQueryEventHandlerT4201:
    data_flag = False
    def OnReceiveData(self, code):
        print("리시브 데이터 상태점검 : ", code)
        XAQueryEventHandlerT4201.data_flag = True