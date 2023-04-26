<template>
  <div>
    <b-card class="mb-3" style="width: 600px; margin-left: 10px; margin-top: 10px;" img-left>
      <b-row>
        <b-col>
          <img v-if="!avatar_computed" :src="require('@/assets/default_user.png')"
               width="200px" height="300px">
          <img v-if="avatar_computed" :src="avatar_computed" width="200px" height="300px">
        </b-col>
        <b-col>
          <b-card-body :title="full_name">
            <b-card-text>
              <b-row v-if="email">
                <span class="text-muted">Почта:&nbsp</span>
                <span>{{ email }}</span>
              </b-row>
              <b-row v-if="login">
                <span class="text-muted">Логин:&nbsp</span>
                <span>{{ login }}</span>
              </b-row>
              <b-row v-if="password">
                <span class="text-muted">Пароль:&nbsp</span>
                <span>{{ password }}</span>
              </b-row>
              <b-row>
                <router-link to="/report">Сгенерировать отчет</router-link>
              </b-row>
            </b-card-text>
          </b-card-body>
<!--          <a v-on:click="edit_profile" style="color:dodgerblue; cursor: pointer;" >редактировать профиль</a>-->
        </b-col>
      </b-row>
    </b-card>

    <div style="margin-top: 10px">
      <h4 align="center">Недавно просмотренное:</h4>
      <div>
        <PreviewCollection
          v-bind:filters="filters">
        </PreviewCollection>
      </div>
    </div>

  </div>
</template>

<script>
import {log_event} from '@/services/scouting'
import PreviewCollection from "@/components/PreviewCollection.vue";
import {fillUserInfo} from "@/services/repositories/user";

export default {
  data() {
    return {
      name: '',
      last_name: '',
      email: '',
      login: '',
      password: '',
      avatar: '',
      filters: {
        'recent_viewed': true
      }
    }
  },

  computed: {
    avatar_computed() {
      if (!this.avatar) return null
      return this.avatar
    },

    full_name() {
      return this.name + ' ' + this.last_name
    }
  },

  created() {
    log_event('view_account')

    let fill = (data) => {
      this.name = data.name;
      this.last_name = data.last_name;
      this.email = data.email;
      this.login = data.login;
      this.password = data.password;
      this.avatar = data.avatar;
    }

    let data = this.$store.state.account.user_info;
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

  methods: {
    edit_profile() {
      this.$router.push({ name: 'edit_profile'})
    }
  },

  components: {
    PreviewCollection
  },
};
</script>
