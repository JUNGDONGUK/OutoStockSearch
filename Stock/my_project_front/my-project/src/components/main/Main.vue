<template>
    <section v-if='isload'>
        <PopupAccount :accountList='accountList'/>
        <nav class="search-wrapper">
            <select id="stockCategory" class="search">
                <option>전체</option>
                <option>코스피</option>
                <option>코스닥</option>
            </select>
            <input id="stockName" type="text" class="search" placeholder="종목을 검색하세요">
            <button class="search-button" @click="stockSearch">종목 검색</button>
        </nav>
        <article @click="popupStockDetail(stock)" style="cursor: pointer;" class='stock-list'   :key="stock" v-for="stock in stockList">
            <div>
                <span>종목명:</span>
                <span>{{ stock.hname }}</span>
            </div>
            <div>
                <span>종목번호:</span>
                <span>{{ stock.shcode }}</span>
            </div>
            <br/>
            <div>
                <span>기준가:</span>
                <span>{{ stock.recprice }}</span>
            </div>
            <div>
                <span>상한가:</span>
                <span>{{ stock.uplmtprice }}</span>
            </div>
            <div>
                <span>하한가:</span>
                <span>{{ stock.dnlmtprice }}</span>
            </div>
            <div class="line"></div>
        </article>
        <PopupStock :stock_title='title' :chartData='chartData' :options='options' v-show='show' @closePopup='closePopup'/>
    </section>
</template>

<script>
import PopupStock from '@/components/popup/PopupStock.vue';
import PopupAccount from '@/components/popup/PopupAccountList.vue';

export default {
    data () {
        return {
            title: '샘플 종목',
            chartData: [['Date', 'Low', 'Open', 'Close', 'High']],
            options: {
                legend: 'none',
                series: {
                    0: { color: '#a561bd' },
                    1: { color: '#c784de' },
                    2: { color: '#f1ca3a' },
                    3: { color: '#2980b9' },
                    4: { color: '#e67e22' }
                }
            },
            show: false,
            now_cost: '',
            start_cost: '',
            end_cost: '',
            stockList: [],
            accountList: this.$session.get('accountList'),
            accountNum: this.$session.get('userAccountNum'),
            isload: false,
            shcode: '',
            gubun: 2,
            ncnt: 1,
            qrycnt: 500,
            sdate: this.$moment(new Date()).add(-499, 'days').format('YYYYMMDD'),
            edate: this.$moment(new Date()).format('YYYYMMDD')
        };
    },
    components: {
        PopupStock,
        PopupAccount
    },
    created () {
        if ((this.$session.get('userId') === undefined) || (this.$session.get('accountList') === undefined)) {
            this.userCheck();
        } else {
            this.isload = true;
        }
    },
    methods: {
        popupStockDetail (stock) {
            this.title = stock.hname;
            this.shcode = stock.shcode;
            alert('차트가져온다잇! : ' + this.title + ' // ' + this.shcode + ' // ' + this.sdate + ' // ' + this.edate);
            let formData = new FormData();
            formData.append('shcode', this.shcode);
            formData.append('gubun', this.gubun);
            formData.append('ncnt', this.ncnt);
            formData.append('qrycnt', this.qrycnt);
            formData.append('sdate', this.sdate);
            formData.append('edate', this.edate);
            this.$Axios.post(`${process.env.APIURL}/stockDetail/`, formData)
                .then(response => {
                    let data = response.data;
                    console.log(data);
                    if (data.status === 'SUCCESS') {
                        alert('SUCCESS');
                        for (var i = 0; i < data.data.length; i++) {
                            var stockDate = data.data[i].stock_date;
                            var stockLow = data.data[i].stock_low *= 1;
                            var stockOpen = data.data[i].stock_open *= 1;
                            var stockClose = data.data[i].stock_close *= 1;
                            var stockHigh = data.data[i].stock_high *= 1;
                            var stockChartData = [stockDate, stockLow, stockOpen, stockClose, stockHigh];
                            // data.data[i]['stock_date'], data.data[i]['stock_low'], data.data[i]['stock_open'], data.data[i]['stock_close'], data.data[i]['stock_high']];
                            this.chartData.push(stockChartData);
                        }
                        console.log(this.chartData);
                    } else {
                        alert(`${data.error}`);
                    }
                });
            this.show = true;
        },
        closePopup () {
            this.show = false;
        },
        userCheck () {
            this.$Axios.post(`${process.env.APIURL}/login/`)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        // Vue의 server session에 데이터 담아주기
                        if (data.data.user_id === null || data.data.accounts === null) {
                            alert('비정상적인 접근입니다. 로그인을 진행해주세요');
                            this.$router.push('/login');
                        }
                        this.$session.set('userId', data.data.user_id);
                        this.$session.set('accountList', data.data.accounts);
                        this.$nextTick(function () {
                            location.reload();
                        });
                    } else {
                        alert(`${data.error}`);
                        document.getElementById('loginId').value = '';
                        document.getElementById('loginPassword').value = '';
                        document.getElementById('loginCertPassword').value = '';
                    }
                });
        },
        stockSearch () {
            var stockCategory = document.getElementById('stockCategory').value;
            if (stockCategory === '전체') {
                stockCategory = 0;
            } else if (stockCategory === '코스피') {
                stockCategory = 1;
            } else {
                stockCategory = 2;
            }
            var stockName = document.getElementById('stockName').value;
            this.$Axios.get(`${process.env.APIURL}/stocksearch/?stockCategory=${stockCategory}&stockName=${stockName}`)
                .then(response => {
                    let data = response.data;
                    console.log(data);
                    if (data.status === 'SUCCESS') {
                        this.stockList = data.data;
                    }
                });
        }
    }
};
</script>

<style>
    .stock-list {
        margin: 0px auto;
        position: relative;
        background-color: white;
        width: 55%;
        height: 60px;
        text-align: center;
        margin-top: 30px;
        border: solid black;
        padding-top: 38px;
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
        font-weight: bold;
    }
    .stock-list:hover {
        background-color: #009aff;
    }
    .stock-list > div {
        display: inline;
    }
    .search-wrapper{
        margin-top: 30px;
        text-align: center;
    }
    .search{
        width: 400px;
        height: 48px;
        margin: 0px auto;
        display: inline;
    }
    .search-button{
        width: 226px;
        height: 56px;
        font-weight: bold;
        background-color: #19ce60;
        border: 1px solid #15c654;
        color: blanchedalmond;
        font-size: larger;
        vertical-align: middle;
    }
    .line{
        background-color: gray;
        height: 10px;
        clear:both;
    }
</style>
