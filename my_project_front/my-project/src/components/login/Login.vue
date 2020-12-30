<template>
    <section>
        <article class='login-wrapper' v-if="!isLoading">
            <div class="input_pack">
                <input type="text" placeholder="아이디를 입력해주세요" id='loginId' class="login id" v-model="loginId" title="아이디입력">
            </div>
            <div class="input_pack">
                <input type="password" maxlength=8 placeholder="비밀번호를 입력해주세요" id='loginPassword' class="login password" v-model="loginPassword" title="패스워드입력">
            </div>
            <div class="input_pack">
                <input type="password" placeholder="인증서 비밀번호를 입력해주세요" id='loginCertPassword' class="login certPassword" v-model="loginCertPassword" title="패스워드입력">
            </div>
            <button class="login-button" @click="doLogin">로그인</button>
        </article>
        <div id='loadingBar' v-if="isLoading"> <!--  -->
            <img src='../../../dist/img/lodingBar.gif'/>
        </div>
    </section>
</template>

<script>

export default {
    data () {
        return {
            loginId: '',
            loginPassword: '',
            loginCertPassword: '',
            show: false,
            isLoading: false
        };
    },
    created () {
        this.$session.get('userId') !== null ? this.$session.clear() : this.$session.get('accountList') !== null ? this.$session.clear() : this.$router.push('/');
    },
    methods: {
        idCheack () {
            alert('아이디를 입력하지 않으셨습니다. 아이디를 입력해주세요.', () => {
                document.getElementById('loginId').focus();
                this.isLoading = false;
                return false;
            });
        },
        pwCheack () {
            alert('비밀번호를 입력하지 않으셨습니다. 비밀번호를 입력해주세요.', () => {
                document.getElementById('loginPassword').focus();
                this.isLoading = false;
                return false;
            });
        },
        loginCheack () {
            console.log('접속을 환영합니다.');
        },
        doLogin () {
            this.isLoading = true;
            document.getElementsByTagName('body')[0].style.overflow = 'hidden';
            (this.loginId === '') ? this.idCheack() : (this.loginPassword === '') ? this.pwCheack() : this.loginCheack();
            let loginId = this.loginId.trim();
            let loginPw = this.loginPassword.trim();
            let loginCertPassword = this.loginCertPassword.trim();
            let formData = new FormData();
            formData.append('userId', loginId);
            formData.append('userPw', loginPw);
            formData.append('userCertPassword', loginCertPassword);
            // 정상적으로 formData에 들어가느니것 확인
            this.$Axios.post(`${process.env.APIURL}/login/`, formData, { withCredentials: true })
                .then(response => {
                    let data = response.data;
                    if (data.status === 'SUCCESS') {
                        // Vue의 server session에 데이터 담아주기
                        // TODO
                        // 배포하고 싶다면 pw들은 암호화 처리해야된다.
                        this.$session.set('userId', loginId);
                        this.$session.set('accountList', data.data.accounts);
                        this.$nextTick(function () {
                            this.$router.push('/');
                        });
                    } else {
                        this.isLoading = false;
                        alert(`${data.error}`);
                        document.getElementById('loginId').value = '';
                        document.getElementById('loginPassword').value = '';
                        document.getElementById('loginCertPassword').value = '';
                    }
                });
        },
        makeLoadingBar () {

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
    #loadingBar {
        z-index: 999999;
        position: absolute;
        text-align: center;
        margin: auto;
        width: 98vw;
        height: 98vh;
    }
    img {
        margin-top: 15%;
        width: 200px;
        height: 200px;
        object-fit: cover;
    }

</style>
