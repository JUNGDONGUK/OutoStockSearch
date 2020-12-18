import Vue from 'vue';
import Router from 'vue-router';
import Main from '@/components/main/Main.vue';
import TopTransactionCrawling from '@/components/account/TopTransactionCrawling.vue';
import Login from '@/components/login/Login.vue';
import SystemTradding from '@/components/tradding/SystemTradding.vue';

Vue.use(Router);

export default new Router({
    routes: [
        {
            path: '/',
            name: 'mainPage',
            component: Main,
            meta: {
                accountList: ''
            }
        },
        {
            path: '/transactiondetails',
            name: 'transactionDetails',
            component: TopTransactionCrawling
        },
        {
            path: '/login',
            name: 'loginPage',
            component: Login
        },
        {
            path: '/systemtradding',
            name: 'systemTradding',
            component: SystemTradding
        }
    ]
});
