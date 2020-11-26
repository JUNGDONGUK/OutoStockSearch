// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import router from './router';
import VueSession from 'vue-session';
import axios from 'axios';

// Axios 설정
Vue.prototype.$Axios = axios;
// 응답 시간 설정
axios.defaults.timeout = 20000;
// 세션 세팅
var sessionOptions = {
    persist: true
};
Vue.use(VueSession, sessionOptions);
// 기본 Vue 세팅
Vue.config.productionTip = false;
/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    components: { App },
    template: '<App/>'
});
