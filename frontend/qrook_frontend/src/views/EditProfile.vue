<template>
  <div>
    <span class="before"></span>
    <div
      class="d-flex align-items-center justify-content-center"
      style="width: 100%; height: 100%; display: inline-block; vertical-align: middle;">
      <b-form @submit="on_submit">

        <b-form-group id="input-group-7" label="Фото:" label-for="input-7"
                      label-align="right" content-cols="8">
          <b-form-file
            style="max-width: 400px"
            id="file"
            placeholder="Выберите фото"
          ></b-form-file>
        </b-form-group>

        <b-form-group id="input-group-1" label="Имя:" label-for="input-1"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-1"
            v-model="form.name"
            placeholder="Введите имя"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-6" label="Фамилия:" label-for="input-6"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-6"
            v-model="form.last_name"
            placeholder="Введите фамилию"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-2" label="Логин:" label-for="input-2"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-2"
            v-model="form.login"
            placeholder="Введите логин"
            required
            disabled
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-3" label="Эл. почта:" label-for="input-3"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-3"
            v-model="form.email"
            type="email"
            placeholder="Введите эл. почту"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-4" label="Текущий пароль:" label-for="input-4"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-4"
            aria-describedby="input-live-help password-feedback"
            v-model="form.old_password"
            placeholder="Введите текущий пароль"
            type="password"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group id="input-group-4" label="Новый пароль:" label-for="input-4"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-4"
            :state="check_password"
            aria-describedby="input-live-help password-feedback"
            v-model="form.new_password"
            placeholder="Введите новый пароль"
            type="password"
          ></b-form-input>
          <div v-if="this.form.new_password.length === 0" class="text-muted" style="font-size: 14px">*Не заполняйте,
            если не хотите менять пароль
          </div>
          <b-form-invalid-feedback id="password-feedback">
            Пароль должен быть не короче 6 символов
          </b-form-invalid-feedback>
        </b-form-group>

        <b-form-group id="input-group-5" label="Подтвердите новый пароль:" label-for="input-5"
                      label-align="right" content-cols="8">
          <b-form-input
            id="input-5"
            :state="check_password_eq"
            aria-describedby="input-live-help password-eq-feedback"
            v-model="form.repeated_password"
            placeholder="Введите пароль еще раз"
            type="password"
          ></b-form-input>

          <b-form-invalid-feedback id="password-eq-feedback">
            Пароли должны совпадать
          </b-form-invalid-feedback>
        </b-form-group>

        <p class="error_logging" v-if="failed"> Некорректный пароль </p>

        <b-button type="submit" value="update" block variant="primary">Обновить профиль</b-button>
        <b-button type="submit" value="delete" block variant="danger">Удалить профиль</b-button>
        <div>
          <a v-on:click="$router.go(-1)" style="color:black; cursor: pointer;">отмена</a>
        </div>
      </b-form>
    </div>
  </div>
</template>

<script>
import {log_event} from '@/services/scouting'
import {user_repo, fillUserInfo} from "@/services/repositories/user";
import {reset_token} from "../services/http";

export default {
  data() {
    return {
      form: {
        name: '',
        last_name: '',
        email: '',
        login: '',
        old_password: '',
        new_password: '',
        repeated_password: ''
      },
      failed: '',
    }
  },

  created() {
    let data = this.$store.state.account.user_info;

    let fill = (data) => {
      this.form.name = data.name;
      this.form.last_name = data.last_name;
      this.form.email = data.email;
      this.form.login = data.login;
    }

    if (!data) {
      fillUserInfo(this)
      setTimeout(() => {
        data = this.$store.state.account.user_info;
        fill(data)
      }, 1000)
    } else {
      fill(data)
    }
  },

  computed: {
    check_password() {
      return this.form.new_password.length === 0 || this.form.new_password.length >= 6
    },
    check_password_eq() {
      return this.form.new_password === this.form.repeated_password
    }
  },

  methods: {
    on_delete: function (event) {
      event.preventDefault();
      let callback = (userDelete) => {
          this.failed = userDelete.reason;
          if (this.failed) return;

          this.$store.dispatch('account/logout')
          log_event('register')
          setTimeout(reset_token, 3000)
          this.$router.push('main');
      }

      if (confirm('Вы уверены, что хотите удалить аккаунт?')) {
        if (confirm('... точно уверены?')) {
          user_repo.delete_profile(callback);
        }
      }
    },

    on_submit: function (event) {
      event.preventDefault()
      let action = event.submitter.value
      if (action === 'delete') {
        this.on_delete(event)
        return
      }

      let data = new FormData()
      let imagefile = document.querySelector('#file')
      data.append('avatar', imagefile.files[0])
      data.append('name', this.form.name)
      data.append('last_name', this.form.last_name)
      data.append('email', this.form.email)
      data.append('login', this.form.login)
      data.append('password', this.form.old_password)
      data.append('new_password', this.form.new_password)

      let callback = (userUpdate) => {
          this.failed = userUpdate.reason;
          if (this.failed) return;

          fillUserInfo(this)
          log_event('edit_profile')
          this.$router.push('main');
      }

      user_repo.update_profile(data, callback);
    },
  }
}
;
</script>
