<template>
    <section id='accountSection' v-if="isLoad">
        <article class='login-wrapper' v-show='!isConnect'>
            <div class="input_pack">
                <select id="accountNum" class="login accountNum">
                    <option :value="account" v-for="account in accountList" :key="account">{{ account }} {{ accountNum1111 }}</option>
                </select>
            </div>
            <div class="input_pack">
                <input type="password" placeholder="비밀번호를 입력해주세요" id='accountPw' class="login accountPassword" v-model="accountPw" title="패스워드입력">
            </div>
            <button class="login-button" @click="accountConnect">계좌 데이터 확인</button>
        </article>
        <article v-show='isConnect'>
                <li>
                    계좌 번호 : {{ accountNum }}
                    계좌 잔고 : {{ accountNum }}
                    계좌 수익금 : {{ accountNum }}
                    계좌 수익률 : {{ accountNum }}
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
            isConnect: false,
            accountNum: this.$session.get('accountNum'),
            accountPw: '',
            isLoad: false
        };
    },
    created () {
        this.isLoad = true;
    },
    methods: {
        accountConnect () {
            let selectedAccountNum = document.getElementById('accountNum').value;
            let selectedAccountPw = document.getElementById('accountPw').value;
            let formData = new FormData();
            formData.append('userId', this.$session.get('userId'));
            formData.append('userPw', this.$session.get('userPw'));
            formData.append('userCertPassword', this.$session.get('userCertPassword'));
            formData.append('accountNum', selectedAccountNum);
            formData.append('accountPw', selectedAccountPw);
            this.$Axios.post(`${process.env.APIURL}/account/`, formData)
                .then(response => {
                    let popData = response.data;
                    if (popData.status === 'SUCCESS') {
                        this.$session.set('accountNum', selectedAccountNum);
                        this.$session.set('accountPw', selectedAccountPw);
                        alert('SUCCESS');
                    } else {
                        alert('LOGINCHEACKFAIL');
                        this.$router.push('/login');
                    }
                });
        }
    }
};
</script>

<style>
    .login-wrapper{
        margin-top: 100px;
        text-align: center;
    }
    .login{
        margin-top: 10px;
        width: 460px;
        height: 48px;
    }
    .login-button{
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
