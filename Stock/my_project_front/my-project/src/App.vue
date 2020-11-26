<template>
  <div id="app">
    <header>
        <Header/>
    </header>
    <article>
        <router-view/>
    </article>
  </div>
</template>

<script>
import Header from '@/components/common/Header.vue';

export default {
    name: 'App',
    components: {
        Header
    }
};
</script>
