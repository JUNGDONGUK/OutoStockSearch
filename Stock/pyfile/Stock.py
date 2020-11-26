import SysLogging
from SysLogging import writeLog 
class SysTrader():
    def __init__(self):
        """자동투자시스템 메인 클래스
        """
        writeLog()
        self.hello()

    def hello(self):
        print("Hello World!")

SysTrader()