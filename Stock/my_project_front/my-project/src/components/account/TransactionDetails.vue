<template>
    <section>
        <article @click="popupTransactionDetail()" style="cursor: pointer;" class='stock-list'>
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
    </section>
</template>

<script>
export default {
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
