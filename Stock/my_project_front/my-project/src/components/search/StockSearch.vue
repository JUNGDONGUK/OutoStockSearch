<template>
    <section id='searchSection' v-if="isLoad">
        <!-- <PopupAccount :accountList='accountList'/> -->
        <nav class="search-wrapper">
            <select v-model="stockCategoryId" class="search">
                <option>전체</option>
                <option>코스피</option>
                <option>코스닥</option>
            </select>
            <input v-model="stockNameId" type="text" class="search" placeholder="종목을 검색하세요">
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
            stockNameId: '',
            stockCategoryId: '전체',
            chartData: [],
            stockList: [],
            isLoad: false,
            // eslint-disable-next-line
            // isLoad: (!this.$session.get('userAccountNum')) ? false : true,
            show: false,
            shcode: '',
            gubun: 2,
            ncnt: 1,
            qrycnt: 500,
            sdate: this.$moment(new Date()).add(-499, 'days').format('YYYYMMDD'),
            edate: this.$moment(new Date()).format('YYYYMMDD')
        };
    },
    created () {
        // this.stockSearch();
        if (!this.$session.get('userProperty')) {
            this.isLoad = false;
        } else {
            this.isLoad = true;
        }
    },
    components: {
        PopupStock
        // PopupAccount
    },
    methods: {
        stockSearch () {
            let stockCategory = 0;
            switch (this.stockCategoryId) {
            case '코스피': stockCategory = 1; break;
            case '코스닥': stockCategory = 2; break;
            default : stockCategory = 0;
            }
            console.log('목록조회 시작 cate : ' + stockCategory);
            let formData = new FormData();
            formData.append('stockCategory', stockCategory);
            formData.append('stockName', this.stockNameId);
            console.log('왜 안나오지? 01');
            // this.$Axios.get(`${process.env.APIURL}/stocksearch/${stockCategory}/${this.stockNameId}/`)
            this.$Axios.post(`${process.env.APIURL}/stocksearch/`, formData)
                .then(response => {
                    console.log('왜 안나오지? 02');
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        console.log('왜 안나오지? 03');
                        this.stockList = data.data;
                        console.log(this.stockList);
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
