<template>
    <section v-if='isload'>
        <PopupAccount :accountList='accountList'/>
        <StockSearch @forceLogout="forceLogout"/>
        <!-- :options='options' -->
    </section>
</template>

<script>
import PopupAccount from '@/components/popup/PopupAccountList.vue';
import StockSearch from '@/components/search/StockSearch.vue';

export default {
    data () {
        return {
            accountList: this.$session.get('accountList')
        };
    },
    components: {
        PopupAccount,
        StockSearch
    },
    created () {
        if ((this.$session.get('userId') === undefined) || (this.$session.get('accountList') === undefined)) {
            alert('체크하긴한다.');
            this.userCheck();
        } else {
            this.isload = true;
        }
    },
    methods: {
        userCheck () {
            this.$Axios.post(`${process.env.APIURL}/login/`)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        // Vue의 server session에 데이터 담아주기
                        if (data.data.user_id === null || data.data.accounts === null) {
                            alert('로그인을 먼저 진행해주세요');
                            this.$router.push(`/login`);
                        }
                        this.$session.set('userId', data.data.user_id);
                        this.$session.set('accountList', data.data.accounts);
                        this.$nextTick(function () {
                            this.$forceUpdate();
                        });
                    } else {
                        alert(`${data.error}`);
                    }
                });
        },
        forceLogout () {
            alert('로그인 페이지로 이동합니다.');
            this.$session.clear();
            this.$Axios.get(`${process.env.APIURL}/logout/`)
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        alert('이동하긴해');
                        this.$router.push(`/login`);
                    } else {
                        alert(`${data.error}`);
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
