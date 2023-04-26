<template>
  <div>
    <div>
      <img src="@/assets/qrook.png" width="30%">
    </div>
    <div style="display: inline-block; max-width: 500px; margin-top: 50px; font-size: 20px">
      QRook помогает вам быстро найти книги на нужном языке и в удобном формате.
      Используйте возможности группировки книг по сериям, авторам и жанрам для эффективного
      поиска.
    </div>

    <div style="margin-top: 50px">
      <b-button variant="primary" size="lg" v-on:click="go_main">Начать пользоваться</b-button>
    </div>
    <h2></h2>
  </div>
</template>

<script>
export default {
  name: 'Home',

  methods: {
    go_main() {
      this.$emit('from_home');
      this.$router.push('main').catch(()=>{})
    }
  }
};
</script>

