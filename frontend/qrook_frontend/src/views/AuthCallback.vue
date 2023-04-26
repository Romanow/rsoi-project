<template>
  <div>
    Это страница для обработки OIDC-запроса. Если вы ее видите - запрос на авторизацию был завершен с ошибкой.
  </div>
</template>

<script>
import {set_token} from '@/services/http';
import {log_event} from '@/services/scouting';
import {user_repo, fillUserInfo} from '@/services/repositories/user';

export default {
  data() {
    return {};
  },

  computed: {},

  created() {
    let query = this.$route.query

    let callback = (tokenResponse) => {
      if (!tokenResponse.ok) return;

      set_token(tokenResponse.id_token);
      this.$store.dispatch('account/login')
      fillUserInfo(this)
      log_event('login')
      this.checkToken()
    }

    user_repo.get_token(query.code, callback)
  },

  mounted() {
    this.checkToken()
  },

  methods: {
    checkToken() {
      let token = localStorage.getItem('auth_token')
      console.log(token)
      if (token) this.$router.push('/main').catch(() => {});
    }
  },

};
</script>
