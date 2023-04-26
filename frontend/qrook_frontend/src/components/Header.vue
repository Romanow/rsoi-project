<template>
  <div style="height: 10%;" class="bg-secondary">
    <b-row class="text-center" align-v="center" align-h="center" style="max-width: 100%">
      <b-col cols="3">
        <img src="@/assets/qrook_white.png" v-on:click="go_home"
             style="height:75px; cursor:pointer">
      </b-col>

      <b-col cols="7">
        <b-row>
          <b-col cols="5" v-if="show_search">
            <b-form-input v-model="search" placeholder="Поиск" @keyup.enter="enterClicked"></b-form-input>
          </b-col>
          <b-col cols="2">
            <b-button v-on:click="setSearch" type="submit" ref="header_search_btn"><b>Найти</b></b-button>
          </b-col>

          <b-col cols="2">
            <b-button v-b-toggle.filter-sidebar v-on:click="$emit('receive_search', search)"><b>Фильтры</b></b-button>
            <!--<b-button v-on:click="show"><b>Фильтры</b></b-button>-->
            <FilterSidebar
              @set_search="set_search"
              v-bind:search="search"
            ></FilterSidebar>
          </b-col>

        </b-row>
      </b-col>

      <b-col cols="2" class="my-2">
        <b-row align-h="center">
          <b-button pill variant="primary" v-if="!show_account" v-on:click="login" class="my-2">Войти</b-button>
          <b-col v-if="show_account">
            <b-avatar button id="popover-target-1" size="60px"></b-avatar>

            <b-popover target="popover-target-1" triggers="hover" placement="bottom" boundary-padding="1">
              <b-card>
                <b-col>
                  <p>{{ full_name }}</p>
                  <router-link to="/account">Профиль</router-link>
                  <a class="primary-color" v-on:click="logout" style="cursor: pointer;">Выйти</a>
                </b-col>
              </b-card>
            </b-popover>
          </b-col>
        </b-row>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {log_event} from '@/services/scouting'
import FilterSidebar from "@/components/FilterSidebar.vue";
import {reset_token} from "@/services/http";
import {fillUserInfo} from "@/services/repositories/user";

export default {
  name: "Header",

  data() {
    return {
      search: '',
      show_search: true,
    }
  },

  computed: {
    user_info() {
      return this.$store.state.account.user_info;
    },
    logged_in() {
      return this.$store.state.account.logged_in;
    },
    name() {
      if (!this.user_info) return null;
      return this.user_info.name;
    },
    last_name() {
      if (!this.user_info) return null;
      return this.user_info.last_name;
    },
    avatar() {
      if (!this.user_info) return null;
      return this.user_info.avatar;
    },

    show_account: function () {
      return this.logged_in
    },
    full_name: function () {
      return this.name + ' ' + this.last_name
    },
  },

  created() {
    let token = localStorage.getItem('auth_token')
    if (token !== null) {
      this.$store.dispatch('account/login')
      fillUserInfo(this)
    }
  },

  methods: {
    enterClicked() {
      this.$refs.header_search_btn.click()
    },
    set_search(s) {
      this.search = s
    },
    go_home() {
      this.search = ''
      this.$emit("clear_filters");
      this.$router.push('/main').catch(()=>{})
    },
    setSearch() {
      this.$emit("clear_filters");  // significant! restore flags like 'search_books=True' for text-filter to work
      //this.$store.dispatch('filters/extend_filters', {search: this.search})
      this.$store.dispatch('filters/set_search', this.search)
      log_event('searching', {search: this.search})
    },

    login() {
      this.$router.push('/auth')
    },
    logout() {
      log_event('logout')
      reset_token()
      this.$store.dispatch('account/logout')
    },
  },

  components: {
    FilterSidebar
  },
};
</script>
