<template>
    <section id='accountSection'>
        <article class='account-wrapper' v-show='!isConnect'>
            <div class="input_pack">
                <select id="accountNum" class="account accountNum">
                    <option :value="account" :key="account" v-for="account in accountList">{{ account }} {{ accountNum }}</option>
                </select>
            </div>
            <div class="input_pack">
                <input type="password" placeholder="비밀번호를 입력해주세요" id='accountPw' class="account accountPassword" v-model="accountPw" title="패스워드입력">
            </div>
            <button class="account-button" @click="accountConnect">계좌 데이터 확인</button>
        </article>
        <article v-show='isConnect'>
                <li>
                    추정자산 : {{ this.responseData.estimatedNetWorth }}
                    매입금액 : {{ this.responseData.evaluationPNL }}
                    평가손익 : {{ this.responseData.evaluationRateOfReturnByStock }}
                    평가 수익율 : {{ this.responseData.realProfit }}
                    실현손익 : {{ this.responseData.realRateOfReturnByStock }}
                    실현 수익율 : {{ this.responseData.totalPrice }}
                </li>
        </article>
    </section>
</template>

<script>
export default {
    props: ['accountList'],
    data () {
        return {
            isChecked: false,
            accountPassword: '',
            isConnect: true,
            accountNum: this.$session.get('accountNum'),
            accountPw: '',
            responseData: []
        };
    },
    created () {
        if (this.$session.get('userAccountNum') === undefined) {
            this.isConnect = false;
        }
    },
    methods: {
        accountConnect () {
            let selectedAccountNum = document.getElementById('accountNum').value;
            let selectedAccountPw = document.getElementById('accountPw').value;
            let formData = new FormData();
            formData.append('accountNum', selectedAccountNum);
            formData.append('accountPw', selectedAccountPw);

            // 원하는 시간 내에 데이터가 넘어오지 않는다면 세션을 초기화해 로그인 페이지로 되돌려보내기
            var timer = window.setTimeout(function () {
                this.sessionClear();
            }.bind(this), 10000);
            this.$Axios.post(`${process.env.APIURL}/account/`, formData)
                .then(response => {
                    let popData = response.data;
                    if (popData.status === 'SUCCESS') {
                        this.$session.set('userAccountNum', selectedAccountNum);
                        this.isConnect = true;
                        this.responseData = popData.data;
                        // 데이터가 정상적으로 넘어왔으므로 setTimeout 종료
                        clearTimeout(timer);
                    } else {
                        alert(`로그인에 실패하였습니다. ${popData.error}`);
                        this.$router.push('/login');
                    }
                });
        },
        sessionClear () {
            alert('로그인 세션이 만료되었습니다.');
            this.$session.clear();
            this.$router.push('/login');
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
