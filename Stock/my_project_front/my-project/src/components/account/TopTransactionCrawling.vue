<template>
    <section>
        <article style="cursor: pointer;" class='stock-list'>
            <table>
                <th id="category">종목 유형</th>
                <th>No</th>
                <th>종목명</th>
                <th>종목코드</th>
                <th>현재가</th>
                <th>전일대비</th>
                <th>등락률</th>
                <th>거래량</th>
                <th>거래대금</th>
                <th>매수호가</th>
                <th>매도호가</th>
                <th>시가총액</th>
                <th>PER</th>
                <th>ROE</th>
                <tr v-for="(crawlingData, index) in tuneDataLists" :key="index" @click="popupStockDetail(crawlingData)">
                    <th class="category-focuse">주의깊게 볼 종목</th>
                    <td>{{ crawlingData.no }}</td>
                    <td>{{ crawlingData.종목명 }}</td>
                    <td>{{ crawlingData.종목코드 }}</td>
                    <td>{{ crawlingData.현재가 }}</td>
                    <td>{{ crawlingData.전일대비 }}</td>
                    <td>{{ crawlingData.등락률 }}</td>
                    <td>{{ crawlingData.거래량 }}</td>
                    <td>{{ crawlingData.거래대금 }}</td>
                    <td>{{ crawlingData.매수호가 }}</td>
                    <td>{{ crawlingData.매도호가 }}</td>
                    <td>{{ crawlingData.시가총액 }}</td>
                    <td>{{ crawlingData.PER }}</td>
                    <td>{{ crawlingData.ROE }}</td>
                </tr>
                <br/><br/><br/><br/><br/>
                <tr v-for="(crawlingData, index) in crawlingLists" :key="index" @click="popupStockDetail(crawlingData)">
                    <th class="category-transaction">거래량 상위 100개 종목</th>
                    <td>{{ crawlingData.no }}</td>
                    <td>{{ crawlingData.종목명 }}</td>
                    <td>{{ crawlingData.종목코드 }}</td>
                    <td>{{ crawlingData.현재가 }}</td>
                    <td>{{ crawlingData.전일대비 }}</td>
                    <td>{{ crawlingData.등락률 }}</td>
                    <td>{{ crawlingData.거래량 }}</td>
                    <td>{{ crawlingData.거래대금 }}</td>
                    <td>{{ crawlingData.매수호가 }}</td>
                    <td>{{ crawlingData.매도호가 }}</td>
                    <td>{{ crawlingData.시가총액 }}</td>
                    <td>{{ crawlingData.PER }}</td>
                    <td>{{ crawlingData.ROE }}</td>
                </tr>
            </table>
        </article>
        <PopupStock :stockTitle='title' :chartData='chartData' :show='show' :stockNo='shcode' v-show='show' @closePopup='closePopup'/>
    </section>
</template>

<script>
import PopupStock from '@/components/popup/PopupStock.vue';
export default {
    data () {
        return {
            title: '',
            chartData: [],
            show: false,
            shcode: '',
            gubun: 2,
            ncnt: 1,
            qrycnt: 500,
            sdate: this.$moment(new Date()).add(-499, 'days').format('YYYYMMDD'),
            edate: this.$moment(new Date()).format('YYYYMMDD'),
            crawlingLists: (!this.$session.get('crawlingLists')) ? [] : this.$session.get('crawlingLists'),
            tuneDataLists: (!this.$session.get('tuneDataLists')) ? [] : this.$session.get('tuneDataLists')
        };
    },
    created () {
        if (!this.$session.get('userId')) {
            alert('로그인을 진행하세요');
            this.$router.push('/login');
        } else {
            if (!this.$session.get('crawlingLists')) {
                this.dataCrawling();
            }
        }
    },
    components: {
        PopupStock
    },
    methods: {
        dataCrawling () {
            this.$Axios.get(`${process.env.APIURL}/webCrawling/`)
                .then(response => {
                    let data = response.data;
                    console.log(data);
                    if (data.status === 'SUCCESS') {
                        this.crawlingLists = data.crawlingList;
                        this.tuneDataLists = data.tuneDataList;
                        this.$session.set('crawlingLists', data.crawlingList);
                        this.$session.set('tuneDataLists', data.tuneDataList);
                        this.$session.set('tuneT4201', data.tuneT4201);
                        this.$nextTick(function () {
                            location.reload();
                        });
                    } else {
                        alert('데이터 조회 중 문제가 발생하였습니다.');
                        this.$router.back();
                    }
                });
        },
        popupStockDetail (stock) {
            console.log('check01');
            this.title = stock.종목명;
            this.shcode = stock.종목코드;
            var dataObj = Object;
            let tuneT4201 = this.$session.get('tuneT4201');
            for (var i = 0; i < tuneT4201.length; i++) {
                if (tuneT4201[i]['shcode'] === this.shcode) {
                    dataObj = tuneT4201[i];
                }
            }
            console.log('check02');
            this.$nextTick(function () {
                console.log('check03');
                console.log(dataObj);
                let formData = new FormData();
                formData.append('shcode', dataObj.shcode);
                formData.append('gubun', this.gubun);
                formData.append('ncnt', this.ncnt);
                formData.append('qrycnt', this.qrycnt);
                formData.append('sdate', this.sdate);
                formData.append('edate', this.edate);
                formData.append('AcntNo', this.$session.get('userAccountNum'));
                formData.append('AccountPw', this.$session.get('userAccountPw'));
                formData.append('IsuNo', dataObj.shcode);
                this.$Axios.post(`${process.env.APIURL}/stockDetail/`, formData)
                    .then(response => {
                        let data = response.data;
                        if (data.status === 'SUCCESS') {
                            for (let i = 0; i < data.data.length; i++) {
                                let stockDate = data.data[i].stock_date;
                                let stockLow = data.data[i].stock_low *= 1;
                                let stockOpen = data.data[i].stock_open *= 1;
                                let stockClose = data.data[i].stock_close *= 1;
                                let stockHigh = data.data[i].stock_high *= 1;
                                let stockChartData = {'stockDate': stockDate, 'stockLow': stockLow, 'stockOpen': stockOpen, 'stockClose': stockClose, 'stockHigh': stockHigh};
                                this.chartData.push(stockChartData);
                            }
                            this.$nextTick(function () {
                                this.show = true;
                                document.getElementsByTagName('body')[0].style.overflow = 'hidden';
                            });
                        } else {
                            alert(`${data.error}`);
                        }
                    });
            });
        },
        closePopup () {
            this.show = false;
            this.chartData = [];
            document.getElementById('chartSvg').innerHTML = '';
        }
    }
};
</script>
<style>
    .stock-list {
        margin-top: 50px;
    }
    tr {
        position: relative;
        background-color: white;
        width: 98.5%;
        height: 60px;
        text-align: center;
        border: solid black 1px;
        border-radius: 2px;
        transition: all .3s ease;
        font-weight: bold;
        margin-top : 30px;
    }
    tr:hover {
        background-color: #c8c8c8;
    }
    table {
        margin-left: auto;
        margin-right: auto;
        margin-top: -0.8%;
    }
    th {
        background-color: antiquewhite;
        width: 7%;
        height: 50px;
        vertical-align: middle;
    }
    .category-focuse{
        background-color: rgb(250, 215, 215);
    }
    .category-transaction{
        background-color: rgb(215, 221, 250);
    }
</style>
