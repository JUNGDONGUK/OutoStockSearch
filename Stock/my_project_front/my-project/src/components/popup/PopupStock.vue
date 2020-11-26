<template>
    <section class="pagepop-wrapper">
        <div class='chart-area'>
            <header class="pagepop-header">
                <button class="pagepop-close" @click='closePopup'>X</button>
                {{ stock_title }}
            </header>
            <article class="pagepop-article">
                차트 데이터 출력<br/>
                {{ stock_data }}
            </article>
            <aside class="pagepop-aside">
                <button class="pagepop-default-button call">매수</button>
                <button class="pagepop-default-button put">매도</button>
                <button class="pagepop-default-button sys">시스템</button> <!-- 클릭 시 알고리즘 목록 표출 -->
            </aside>
        </div>
    </section>
</template>

<script>
export default {
    props: [
        'stock_title', 'stock_detail', 'stock_data'
    ],
    methods: {
        closePopup () {
            this.$emit('closePopup');
            console.log('반응');
        }
    }
};
</script>

<style>
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
        font-family: Georgia, "Malgun Gothic", serif;
        font-size: 1.5rem;
        background-color: #f8f8f8;
        padding-top: 0.8%;
        padding-left: 1%;
    }
    .pagepop-article {
        height: 90%;
        width: 75%;
        padding-top: 1%;
        padding-left: 1%;
        color: black;
        background-color: #c8c8c8;
        float: left;
    }
    .pagepop-aside {
        height: 90%;
        padding-left: 75%;
        padding-top: 1%;
        width: 25%;
        text-align: center;
        background-color: #a8a8a8;
    }
    .pagepop-default-button{
        width: 75px;
        height: 50px;
        border-radius: 5px;
        border: solid 1px;
        font-weight: bold;
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
</style>
