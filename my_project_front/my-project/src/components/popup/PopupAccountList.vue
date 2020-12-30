<template>
    <section id='accountSection'>
        <article class='account-wrapper' v-if="!isConnect">
            <div class="input_pack">
                <select id="accountNum" class="account accountNum">
                    <option :value="account" :key="index" v-for="(account, index) in accountList">{{ account }} {{ accountNum }}</option>
                </select>
            </div>
            <div class="input_pack">
                <input type="password" placeholder="비밀번호를 입력해주세요" id='accountPassword' class="account accountPassword" v-model="accountPassword" title="패스워드입력">
            </div>
            <button class="account-button" @click="accountConnect">계좌 데이터 확인</button>
        </article>
        <article v-if="isConnect">
                <li>
                    추정자산 : {{ this.$session.get('userProperty') }}
                </li>
        </article>
    </section>
</template>

<script>
export default {
    props: ['accountList'],
    data () {
        return {
            accountNum: this.$session.get('userAccountNum'),
            accountPassword: '',
            isConnect: false
        };
    },
    created () {
        if (!this.$session.get('userProperty')) {
            this.isConnect = false;
        } else {
            this.isConnect = true;
        }
    },
    methods: {
        accountConnect () {
            let selectedAccountNum = document.getElementById('accountNum').value;
            let selectedAccountPw = this.accountPassword;
            if (selectedAccountNum === '' || selectedAccountPw === '') {
                alert('계좌번호 또는 비밀번호를 확인해주세요');
                return false;
            }
            let formData = new FormData();
            formData.append('accountNum', selectedAccountNum);
            formData.append('accountPw', selectedAccountPw);
            this.$Axios.post(`${process.env.APIURL}/account/`, formData, { withCredentials: true })
                .then(response => {
                    let popData = response.data;
                    if (popData.status === 'SUCCESS') {
                        console.log('accountConnect 성공');
                        console.log(popData.userProperty);
                        this.$session.set('userProperty', popData.userProperty);
                        this.$session.set('userAccountNum', selectedAccountNum);
                        this.$session.set('userAccountPw', this.accountPassword);
                        this.isConnect = true;
                        this.$forceUpdate();
                        this.$nextTick(function () {
                            location.reload();
                        });
                    } else {
                        if (popData.errorCode === '001') {
                            alert('세션이 만료되었습니다. 로그인을 다시 진행해주세요');
                            this.$nextTick(function () {
                                this.forceLogout();
                            });
                        } else {
                            alert('데이터를 가져오는 도중 오류가 발생하였습니다.\n' + popData.error);
                            this.$nextTick(function () {
                                this.forceLogout();
                            });
                        }
                    }
                });
        },
        forceLogout () {
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
