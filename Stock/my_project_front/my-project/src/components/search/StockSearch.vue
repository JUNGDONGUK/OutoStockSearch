<template>
    <section id='searchSection' v-if="isLoad">
        <!-- <PopupAccount :accountList='accountList'/> -->
        <nav class="search-wrapper">
            <select id="stockCategory" class="search">
                <option>전체</option>
                <option>코스피</option>
                <option>코스닥</option>
            </select>
            <input id="stockName" type="text" class="search" placeholder="종목을 검색하세요">
            <button class="search-button" @click="stockSearch">종목 검색</button>
        </nav>
        <article @click="popupStockDetail(stock)" style="cursor: pointer;" class='stock-list' :key="stockIndex" v-for="(stock, stockIndex) in stockList">
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
        <PopupStock :stockTitle='title' :chartData='chartData' :show='show' :stockNo='shcode' v-show='show' @closePopup='closePopup'/>
    </section>
</template>

<script>
// import PopupAccount from '@/components/popup/PopupAccountList.vue';
import PopupStock from '@/components/popup/PopupStock.vue';
export default {
    data () {
        return {
            title: '',
            chartData: [],
            stockList: [],
            isLoad: false,
            show: false,
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
        PopupStock
        // PopupAccount
    },
    created () {
        alert('목록조회 시작');
        this.stockSearch();
        this.$forceUpdate();
    },
    methods: {
        stockSearch () {
            let stockCategory = 0;
            // if (!(document.getElementById('stockCategory').value)) {
            //     let stockCategory = document.getElementById('stockCategory').value;
            //     if (stockCategory === '전체') {
            //         stockCategory = 0;
            //     } else if (stockCategory === '코스피') {
            //         stockCategory = 1;
            //     } else {
            //         stockCategory = 2;
            //     }
            // } else {
            //     stockCategory = 0;
            // }
            console.log(stockCategory);
            alert('목록조회 시작01 : ' + stockCategory);
            // let stockName = document.getElementById('stockName').value;
            let stockName = '';
            let formData = new FormData();
            formData.append('stockCategory', stockCategory);
            formData.append('stockName', stockName);
            alert('왜 안나오지? 01');
            this.$Axios.post(`${process.env.APIURL}/stocksearch/`, formData)
                .then(response => {
                    alert('왜 안나오지? 02');
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        alert('왜 안나오지? 03');
                        this.stockList = data.data;
                        console.log(this.stockList);
                        this.isLoad = true;
                        this.$forceUpdate();
                    } else {
                        if (data.errorCode === '001') {
                            alert('세션이 만료되었습니다. 로그인을 다시 진행해주세요');
                            this.$emit('forceLogout');
                        } else {
                            alert('데이터를 가져오는 도중 오류가 발생하였습니다.\n' + data.error);
                        }
                    }
                });
        },
        popupStockDetail (stock) {
            this.title = stock.hname;
            this.shcode = stock.shcode;
            let formData = new FormData();
            formData.append('shcode', this.shcode);
            formData.append('gubun', this.gubun);
            formData.append('ncnt', this.ncnt);
            formData.append('qrycnt', this.qrycnt);
            formData.append('sdate', this.sdate);
            formData.append('edate', this.edate);
            formData.append('AcntNo', this.$session.get('userAccountNum'));
            formData.append('AccountPw', this.$session.get('userAccountPw'));
            formData.append('IsuNo', this.shcode);
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
                        console.log('Main에서 찍은 값');
                        console.log(this.chartData);
                        this.$nextTick(function () {
                            this.show = true;
                            document.getElementsByTagName('body')[0].style.overflow = 'hidden';
                        });
                    } else {
                        alert(`${data.error}`);
                    }
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
    .account-wrapper{
        margin-top: 100px;
        text-align: center;
    }
    .account{
        margin-top: 10px;
        width: 460px;
        height: 48px;
    }
    .account-button{
        margin-top: 35px;
        width: 460px;
        height: 56px;
        font-weight: bold;
        background-color: #19ce60;
        border: 1px solid #15c654;
        color: blanchedalmond;
        font-size: larger;
    }
</style>
