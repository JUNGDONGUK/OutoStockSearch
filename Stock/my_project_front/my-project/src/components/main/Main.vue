<template>
  <section>
      <article @click="popupStockDetail()" style="cursor: pointer;" class='stock-list'>
            <div>
                {{ title }}
            </div>
            <div>
                {{ now_cost }}
            </div>
            <div>
                {{ start_cost }}
            </div>
            <div>
                {{ end_cost }}
            </div>
      </article>
      <PopupStock :stock_title='title' :stock_detail='detail' :stock_data='data' v-show='show' @closePopup='closePopup'/>
  </section>
</template>

<script>
import PopupStock from '@/components/popup/PopupStock.vue';

export default {
    data () {
        return {
            title: '샘플 종목',
            detail: '샘플 설명',
            data: {
                lambda: '람다'
            },
            show: false,
            now_cost: '',
            start_cost: '',
            end_cost: '',
            info: {}
        };
    },
    components: {
        PopupStock
    },
    created () {
        this.fetchStockInfo();
    },
    methods: {
        fetchStockInfo () {
            this.info = {
                title: '첫 타이틀',
                detail: '첫 디테일',
                now_cost: '10,000원',
                start_cost: '9,000원',
                end_cost: '11,000원',
                data: '첫 데이타'
            };
            this.title = this.info.title;
            this.detail = this.info.detail;
            this.data = this.info.data;
            this.now_cost = this.info.now_cost;
            this.start_cost = this.info.start_cost;
            this.end_cost = this.info.end_cost;
        },
        popupStockDetail () {
            // TODO
            // 이 title이용해서 해당 title에 해당하는 데이터들 ajax로 불러오기
            this.show = true;
        },
        closePopup () {
            this.show = false;
        }
    }
};
</script>

<style>
    .stock-list {
        position: absolute;
        background-color: white;
        width: 98.5%;
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
</style>
