<template>
    <section class='pagepop-wrapper'>
        <div class='chart-area'>
            <header class='pagepop-header'>
                <button class='pagepop-close' @click='closePopup'>X</button>
                {{ stockTitle }}
            </header>
            <article class='pagepop-article'>
                차트 데이터 출력<br/>
                <svg id="chartSvg"></svg>
                <!-- <GChart type='CandlestickChart' :data='chartData' :options='options'/> -->
            </article>
            <aside class='pagepop-aside'>
                <div class='contents-divide'>
                    <div>비밀번호</div>
                    <input class='price' type="password" v-model="password">
                </div>
                <div class='contents-divide'>
                    <div>
                        가격
                    </div>
                    <span>
                        지정가
                        <input type="checkbox" value="00@" @click="doCheck" :checked='!isCheck'/>
                    </span>
                    <span>
                        시장가
                        <input type="checkbox" value="03@" @click="doCheck" :checked='isCheck'/>
                    </span>
                    <input class='price' type="number" v-model="nowPrice"/>
                </div>
                <div class='contents-divide'>
                    <div>
                        수량
                    </div>
                    <input class='price' type="number" v-model="quantity">
                </div>
                <button class='pagepop-default-button call' @click="callTradding">매수</button>
                <button class='pagepop-default-button put' @click="putTradding">매도</button>
                <table v-if='isTransction'>
                    <caption><h3>실시간 잔고</h3></caption>
                    <thead>
                        <tr>
                            <th>종목명</th>
                            <th>현재가</th>
                            <th>매도가능수</th>
                            <th>수익률</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for='(stock, index) in transactionDetails' :key="index">
                            <td> {{ stock.hname }} </td>
                            <td> {{ stock.price }} </td>
                            <td> {{ stock.mdposqt }}% </td>
                            <td> {{ stock.sunikrt }} </td>
                        </tr>
                    </tbody>
                </table>
            </aside>
        </div>
    </section>
</template>

<script>
// import { GChart } from 'vue-google-charts';
// import DrawingCahrt from '@/DrawingChart.js';
import * as d3 from 'd3';

export default {
    components: {
        // GChart,
        // DrawingCahrt,
        d3
    },
    props: [
        'stockTitle', 'chartData', 'show', 'stockNo'
    ],
    // 'options'
    data () {
        return {
            nowPrice: 0,
            quantity: 0,
            password: '',
            gubun: 0,
            priceType: '00',
            isCheck: false,
            transactionDetails: [],
            isTransction: false
        };
    },
    watch: {
        async show (nowShow) {
            if (nowShow === true) {
                this.drawChart(this.chartData);
            }
        }
        // isTransction () {
        //     this.accountConnect();
        // }
    },
    methods: {
        closePopup () {
            this.nowPrice = 0;
            this.quantity = 0;
            this.password = '';
            this.gubun = 0;
            this.priceType = '00';
            this.isCheck = false;
            this.transactionDetails = [];
            this.$emit('closePopup');
        },
        drawChart (chartData) {
            try {
                let maxIndex = ((chartData.length) - 1);
                this.nowPrice = chartData[maxIndex].stockClose;
                let maxStockPrices = 0;
                let minStockPrices = 999999999999;
                for (let i = 0; i < maxIndex + 1; i++) {
                    let parseDate = d3.utcParse('%Y-%m-%d');
                    let dataData = parseDate(chartData[i].stockDate);
                    chartData[i].stockDate = dataData;
                    if (chartData[i].stockLow < minStockPrices) {
                        minStockPrices = chartData[i].stockLow;
                    }
                    if (chartData[i].stockHigh > maxStockPrices) {
                        maxStockPrices = chartData[i].stockHigh;
                    }
                }
                /*
                    X, Y축 그리기
                    나중에 이걸 동적으로 활용하고 싶으면 화면에서 range값을 받아오면 동적으로 활용가능하겠다.
                    domain 은 데이터의 일반적으로 최소, 최대값으로 설정하고 range 는 표출할 범위의 너비, 높이 픽셀값!!
                */
                let startDate = chartData[0].stockDate;
                let endDate = chartData[maxIndex].stockDate;
                let xScale = d3.scaleTime().domain([startDate, endDate]).range([100, 3000]);
                let yScale = d3.scaleLinear().domain([minStockPrices, maxStockPrices]).range([400, 20]);
                /*
                    위에서 만든 축을 활용해 HTML태그 만들기
                    #chartSvg 안에 g 태그를 생성한다.
                    g 태그는 #chartSvg 태그 안에서 여러 요소들을 그룹화 하는데 사용하는 태그
                    축에 사용되는 여러 막대기나 텍스트들의 집합을 묶어줄 g 태그가 필요
                        x에만 attr이 붙는 이유는 기본적으로 #chartSvg 내부에서 좌표계는 y값이 높을수록 아래로 향하기 때문에 x축의 위치를 변경 #
                        translate 를 이용해서 y축에 대응하는 x값의 위치를 330으로 수정
                */
                let xAxisSvg = d3.select('#chartSvg').append('g').attr('transform', 'translate(0, 400)').attr('id', `xAxis`);
                let yAxisSvg = d3.select('#chartSvg').append('g').attr('id', `yAxis`);
                /*
                    AXIS함수 만들기
                    d3 에서는 완성된 형태의 축을 바로 생성할 수 있는 axis 함수를 제공
                    axis* 계열의 함수는 axisBottom, axisTop, axisRight, axisLeft 가 있는데, 기억하기 쉽게 axis 뒤에 막대기가 튀어나올 방향을 지정하면 된다고 생각하면 쉽다.
                    tickSize는 축마다 달려있는 막대기들을 tick 이라고 하는데, 이 tick의 높이값을 설정(10이면 10픽셀)
                    ticks 는 막대기들이 축에 분포될 양을 설정(10이라고 해서 10개가 분포될 것 같지만 그렇지 않고 함수 내부의 알고리즘에 의해 적절한 개수로 배치)
                */
                let xAxis = d3.axisBottom(xScale).tickSize(30).ticks(30);
                let yAxis = d3.axisRight(yScale).tickSize(30).ticks(30);
                xAxis(xAxisSvg);
                yAxis(yAxisSvg);
                /*
                 봉차트를 생성한다.
                */
                for (let i = 0; i < (maxIndex + 1); i++) {
                    let cData = chartData[i];
                    d3.select('#chartSvg').append('g')
                        .attr('stroke-linecap', 'round')
                        .attr('stroke', 'black')
                        .attr('class', `first${i}`);
                    // 위에 생성한 g태그에 line을 삽입한다.
                    d3.select(`.first${i}`).attr('transform', 'translate(' + xScale(cData.stockDate) + ', 0)');
                    d3.select(`.first${i}`).append('line')
                        .attr('y1', yScale(cData.stockLow))
                        .attr('y2', yScale(cData.stockHigh))
                        .attr('stroke-width', 2)
                        .attr('stroke', 'black');
                    d3.select(`.first${i}`).append('line')
                        .attr('y1', yScale(cData.stockOpen))
                        .attr('y2', yScale(cData.stockClose))
                        .attr('stroke-width', 5)
                        .attr('stroke', cData.stockOpen > cData.stockClose ? 'red' : cData.stockClose > cData.stockOpen ? 'blue' : 'black');
                    d3.select(`.first${i}`).append('title')
                        .text(`${cData.stockDate}
                        Open: ${cData.stockOpen}원
                        Close: ${cData.stockClose}원
                        Low: ${cData.stockLow}원
                        High: ${cData.stockHigh}원`);
                    d3.select(`.yAxis`).style('position', 'fixed');
                }
            } catch (e) {
                alert('차트를 불러오는 도중 다음과 같은 에러가 발생하였습니다 \n' + e.name + '\n' + e.message);
                return this.$forceUpdate();
            }
            return true;
        },
        forceLogout () {
            alert('로그인 세션이 만료되었습니다.');
            this.$session.clear();
            this.$Axios.get(`${process.env.APIURL}/logout/`)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        this.$router.push(`/login`);
                    } else {
                        alert(`${data.error}`);
                    }
                });
        },
        callTradding () {
            alert('매수합니다.' + this.nowPrice);
            this.gubun = 2;
            this.traddingAxios();
        },
        putTradding () {
            alert('매도합니다.' + this.nowPrice);
            this.gubun = 1;
            this.traddingAxios();
        },
        sysTradding () {
            alert('시스템거래를 시작합니다.' + this.nowPrice);
        },
        doCheck () {
            this.isCheck = !this.isCheck;
            if (this.isCheck) {
                this.priceType = '03@';
            } else {
                this.priceType = '00@';
            }
        },
        traddingAxios () {
            let formData = new FormData();
            formData.append('AcntNo', this.$session.get('userAccountNum'));
            formData.append('InptPwd', this.password);
            formData.append('IsuNo', this.stockNo);
            formData.append('OrdQty', this.quantity);
            formData.append('OrdPrc', this.nowPrice);
            formData.append('BnsTpCode', this.gubun);
            formData.append('OrdprcPtnCode', this.priceType);
            this.$Axios.post(`${process.env.APIURL}/tradding/`, formData)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        this.transactionDetails = data.transactionDetails;
                        this.$nextTick(function () {
                            this.$forceUpdate();
                        });
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
        },
        accountConnect () {
            alert('작동');
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
            let timer = window.setTimeout(function () {
                this.forceLogout();
            }.bind(this), 10000);
            setTimeout(
                this.$Axios.post(`${process.env.APIURL}/account/`, formData)
                    .then(response => {
                        let popData = response.data;
                        alert('데이터가져옴');
                        if (popData.status === 'SUCCESS') {
                            alert('성공 : PopupStock : ' + popData.userProperty + '\n 종목정보 : ' + popData.transactionDetails);
                            this.$session.set('userProperty', popData.userProperty);
                            this.transactionDetails = popData.transactionDetails;
                            // 데이터가 정상적으로 넘어왔으므로 setTimeout 종료
                            clearTimeout(timer);
                            this.isTransction = true;
                            this.$forceUpdate();
                        } else {
                            if (popData.errorCode === '001') {
                                alert('세션이 만료되었습니다. 로그인을 다시 진행해주세요');
                                this.forceLogout();
                            } else {
                                alert('데이터를 가져오는 도중 오류가 발생하였습니다.\n' + popData.error);
                                this.forceLogout();
                            }
                        }
                    }), 500);
        }
    }
};
</script>

<style>
    .contents-divide{
        margin-top: 15px;
    }
    #chartSvg {
        width: 5000px;
        height: 1000px;
    }
    .pagepop-wrapper {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, .5);
        display: table-cell;
        vertical-align: middle;
        transition: opacity .3s ease;
    }

    .chart-area {
        width: 80%;
        height: 80%;
        margin: 0px auto;
        margin-top : 3.5%;
        padding: 30px 30px;
        background-color: #fff;
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
    }
    .pagepop-close{
        border: solid black;
        background-color: #f2f2f2;
        width: 25px;
        height: 25px;
        float: right;
    }
    .pagepop-close:hover{
        background-color: #c8c8c8;
    }
    .pagepop-header {
        position: relative;
        height: 7.5%;
        color: black;
        font-family: Georgia, 'Malgun Gothic', serif;
        font-size: 1.5rem;
        background-color: #f8f8f8;
        padding-top: 0.8%;
        padding-left: 1%;
    }
    .pagepop-article {
        height: 90%;
        width: 70%;
        padding-top: 1%;
        padding-left: 1%;
        color: black;
        background-color: #c8c8c8;
        float: left;
        overflow: scroll;
    }
    .pagepop-aside {
        height: 90%;
        padding-left: 70%;
        padding-top: 1%;
        width: 30%;
        text-align: center;
        background-color: #a8a8a8;
    }
    .pagepop-default-button{
        width: 75px;
        height: 50px;
        border-radius: 5px;
        border: solid 1px;
        font-weight: bold;
        margin-top: 15px;
    }
    .pagepop-default-button.call{
        background-color: #ff4040;
    }
    .pagepop-default-button.call:hover{
        background-color: #cf0000;
    }
    .pagepop-default-button.put{
        background-color: #009aff;
    }
    .pagepop-default-button.put:hover{
        background-color: #0400ff;
    }
    .pagepop-default-button.sys{
        background-color: #37b328
    }
    .pagepop-default-button.sys:hover{
        background-color: #0f9500
    }
    .price{
        width: 65%;
        height: 30px;
    }
    table {
        width: 95%;
        margin: auto;
        text-align: center;
        overflow: scroll;
        margin-top: 20px;
    }
    table th {
        border-bottom: 3px solid #c5c5c5;
    }
</style>
