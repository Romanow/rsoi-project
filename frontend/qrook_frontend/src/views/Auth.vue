<template>
  <div>
    <span class="before"></span>
    <div
      class="d-flex align-items-center justify-content-center"
      style="width: 100%; height: 100%; display: inline-block; vertical-align: middle;">
      <b-form @submit="onSubmit">
        <b-form-group id="input-group-1" label="Логин:" label-for="input-1"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-1"
            v-model="form.login"
            placeholder="Введите логин"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-2" label="Пароль:" label-for="input-2"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-2"
            v-model="form.password"
            placeholder="Введите пароль"
            required
          ></b-form-input>
        </b-form-group>

        <p class="error_logging" v-if="failed"> Некорректные логин или пароль </p>

        <b-button type="submit" block variant="primary">Войти</b-button>
        <b-container fluid>
          <router-link to="/register">Зарегистрироваться</router-link>
        </b-container>
      </b-form>
    </div>
  </div>
</template>

<script>
import { set_token } from '@/services/http';
import { log_event } from '@/services/scouting';
import { user_repo, fillUserInfo } from '@/services/repositories/user';

export default {
  data() {
    return {
      form: {
        login: '',
        password: '',
      },
      failed: false,
    };
  },

  computed: {
    isError() {
      return this.failed;
    },
  },

  methods: {
    onSubmit(event) {
      event.preventDefault();
      let callback = (userLogin) => {
          this.failed = !userLogin.ok;
          if (this.failed) return;

          set_token(userLogin.token);
          this.$store.dispatch('account/login')
          fillUserInfo(this)
          log_event('login')
          this.$router.go(-1);   // return to previous page
      }

      user_repo.login(this.form.login, this.form.password, callback)
    },

  },
};
</script>
