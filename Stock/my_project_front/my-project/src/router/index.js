import Vue from 'vue';
import Router from 'vue-router';
import Main from '@/components/main/Main.vue';
import TransactionDetails from '@/components/account/TransactionDetails.vue';
import Login from '@/components/login/Login.vue';
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
            component: TransactionDetails
        },
        {
            path: '/login',
            name: 'loginPage',
            component: Login
        }
    ]
});
