<template>
    <nav>
        <button @click="goHome">HOME</button>
        <button @click="goTransactionDetails">거래 내역 조회</button>
    </nav>
</template>

<script>
export default {
    // 거래 내역 페이지로 이동
    methods: {
        goHome () {
            this.$router.push(`/`);
        },
        goTransactionDetails () {
            this.$router.push(`/transactiondetails`);
        }
    }
};
</script>
<style>
    nav {
        text-align: center;
    }
</style>
