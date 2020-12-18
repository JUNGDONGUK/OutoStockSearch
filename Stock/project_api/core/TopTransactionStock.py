from urllib.request import urlopen
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect,HttpResponse
import json

class NvFinance:
    def finance_crawling(request):
        html = urlopen("https://finance.naver.com/sise/sise_quant.nhn")  
        stock_html = BeautifulSoup(html, "html.parser") 

        crawling_list = []
        print("\n\n\n\n\n\n New ============================================================")
        titles = stock_html.find_all('a', attrs={'class':'tltle'})
        tds = stock_html.find_all('td', attrs={'class':'number'})
        count = 1
        for title in titles:
            crawling_data = {"no": count, "종목명": title.text, "종목코드": title['href'].split('=')[1].strip(), "현재가": "", "전일대비": "", "등락률": "", "거래량": "", "거래대금": "", "매수호가": "", "매도호가": "", "시가총액": "", "PER": "", "ROE": ""}
            value_list = ["현재가", "전일대비", "등락률", "거래량", "거래대금", "매수호가", "매도호가", "시가총액", "PER", "ROE"]
            for i in range(10):
                value = value_list.pop(0)
                tdVal = tds.pop(0).text
                crawling_data[value] = tdVal.strip().replace("\n", "").replace("\t", "").replace(" ", "")
            crawling_list.append(crawling_data)
            count = count + 1
        print(crawling_list)
        # for title in titles:
        #     crawling_data = {"종목명": title.text, "현재가": "", "전일대비": "", "등락률": "", "거래량": "", "거래대금": "", "매수호가": "", "매도호가": "", "시가총액": "", "PER": "", "ROE": ""}
        #     title_list = ["현재가", "전일대비", "등락률", "거래량", "거래대금", "매수호가", "매도호가", "시가총액", "PER", "ROE"]
        #     for td in tds:
        #         td = td.strip()
        #         tdVal = td.text.strip()
        #         crawling_data[title_list.pop(0)] = tdVal
        #     crawling_list.append(crawling_data)
        return HttpResponse(json.dumps({"status": "SUCCESS", "crawlingList": crawling_list}))

#contentarea > div.box_type_l > table > tbody > tr
#contentarea > div.box_type_l > table > tbody