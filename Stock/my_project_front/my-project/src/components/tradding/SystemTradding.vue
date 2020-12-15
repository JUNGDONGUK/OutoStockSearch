<template>
    <section class='pagepop-wrapper' v-if="isload">
        <div>
            <select name="알고리즘 종류" id="algorism" v-model="algorismType">
                <option value="01">단타(5이평 급등주 분석)</option>
                <option value="02">장투(장기 하락 마감 종목)</option>
            </select>
            <button @click="stockSelect">조회</button>
            <button>시스템 트레이딩 시작</button>
        </div>
        <div class="tableSetting">
            <table class="tables">
                <caption><h3>조회된 주식 목록</h3></caption>
                <th>조회된 종목명</th>
                <th>현재가</th>
                <th>거래량</th>
                <th>수익률</th>
                <tr v-for='(stock, index) in stockList' :key="index">
                    <td> {{ stock.stockNm }} </td>
                    <td> {{ stock.nowPrice }} </td>
                    <td> {{ stock.volume }} </td>
                    <td> {{ stock.ratioOfProfit }}% </td>
                </tr>
            </table>
        </div>
        <div id="divide"></div>
        <div class="tableSetting">
            <table class="tables">
                <caption><h3>실보유 주식 목록</h3></caption>
                <th>종목명</th>
                <th>현재가</th>
                <th>매도가능수량</th>
                <th>수익률</th>
                <tr v-for='(trade, index) in traddingList' :key="index">
                    <td> {{ trade.stockNm }} </td>
                    <td> {{ trade.price }} </td>
                    <td> {{ trade.volume }} </td>
                    <td> {{ trade.ratioOfProfit }}% </td>
                </tr>
            </table>
        </div>
    </section>
</template>

<script>
export default {
    data () {
        return {
            algorismType: '',
            stockList: [
                {
                    stockNm: '거래하고싶옹?',
                    nowPrice: '123',
                    volume: '123',
                    ratioOfProfit: '100'
                }
            ],
            traddingList: [{stockNm: '없음', price: '없음', volume: '없음', ratioOfProfit: '없음'}],
            isload: false
        };
    },
    created () {
        if ((this.$session.get('userAccountNum') === undefined) || (this.$session.get('userAccountPw') === undefined)) {
            alert('계좌가 존재하지 않습니다.');
            this.$router.back();
        } else {
            this.isload = true;
            this.fetchUserRetainedItem();
        }
    },
    mounted () {
        this.$forceUpdate();
    },
    methods: {
        fetchUserRetainedItem () {
            let selectedAccountNum = this.$session.get('userAccountNum');
            let selectedAccountPw = this.$session.get('userAccountPw');
            if (selectedAccountNum === '' || selectedAccountPw === '') {
                alert('계좌번호 또는 비밀번호를 확인해주세요');
                return false;
            }
            let formData = new FormData();
            formData.append('accountNum', selectedAccountNum);
            formData.append('accountPw', selectedAccountPw);
            // 원하는 시간 내에 데이터가 넘어오지 않는다면 세션을 초기화해 로그인 페이지로 되돌려보내기
            this.$Axios.post(`${process.env.APIURL}/account/`, formData)
                .then(response => {
                    let popData = response.data;
                    if (popData.status === 'SUCCESS') {
                        alert('성공 : SystemTradding');
                        this.$session.set('userProperty', popData.userProperty);
                        if (popData.userRetainedItem[0] !== undefined) {
                            this.traddingList = popData.transactionDetails;
                        }
                        this.$nextTick(function () {
                            this.$forceUpdate();
                        });
                    } else {
                        if (popData.errorCode === '001') {
                            alert('세션이 만료되었습니다. 로그인을 다시 진행해주세요');
                            this.forceLogout();
                        } else {
                            alert('데이터를 가져오는 도중 오류가 발생하였습니다.\n' + popData.error);
                            this.forceLogout();
                        }
                    }
                });
        },
        forceLogout () {
            alert('로그인 세션이 만료되었습니다.');
            this.$router.push(`/login`);
        },
        stockSelect () {
            let formData = new FormData();
            var sdate = this.$moment(new Date()).add(-30, 'days').format('YYYYMMDD');
            var edate = this.$moment(new Date()).format('YYYYMMDD');
            if (this.algorismType === '02') {
                sdate = this.$moment(new Date()).add(-150, 'days').format('YYYYMMDD');
                edate = this.$moment(new Date()).format('YYYYMMDD');
            }
            formData.append('algorismType', this.algorismType);
            formData.append('sdate', sdate);
            formData.append('edate', edate);
            this.$Axios.post(`${process.env.APIURL}/systemTradding/`, formData)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        alert('성공 : SystemTradding : SUCCESS');
                        this.stockList = data.useStock;
                        this.$forceUpdate();
                        console.log(this.stockList);
                    } else {
                        if (data.errorCode === '001') {
                            alert('세션이 만료되었습니다. 로그인을 다시 진행해주세요');
                            this.forceLogout();
                        } else {
                            alert('데이터를 가져오는 도중 오류가 발생하였습니다.\n' + data.error);
                            this.forceLogout();
                        }
                    }
                });
        }
    }
};
</script>

<style>
    .tableSetting {
        width: 50%;
        position: relative;
        float: left;
        text-align: center;
        margin: auto;
    }
    .pagepop-wrapper {
        text-align: center;
    }
    .tables {
        border-collapse: separate;
        border-spacing: 1px;
        line-height: 1.5;
        border-top: 1px solid #ccc;
        margin: auto 0px;
        text-align: center;
    }
    .tables th {
        width: 150px;
        padding: 10px;
        font-weight: bold;
        vertical-align: top;
        border-bottom: 1px solid #ccc;
    }
    .tables td {
        width: 350px;
        padding: 10px;
        vertical-align: top;
        border-bottom: 1px solid #ccc;
    }
    #divide {
        position:fixed;
        margin-top: 20px;
        margin-left: 49.6%;
        width: 3px;
        height: 100%;
        background-color: gray;
    }
</style>
