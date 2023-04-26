<template>
  <div id="app">

    <Header v-if="enable_header"/>

    <router-view
      @from_home="from_home"
    />
    <footer id="footer" v-if="enable_footer">
      <div>
        Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a
        href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>
      </div>
    </footer>
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import {HTTP} from '@/services/http'
import {set_token} from "./services/http";

export default {
  name: 'App',
  data() {
    return {
      enable_footer: false,
      enable_header: true,
      ignore_push_main: true,
    }
  },

  components: {
    Header
  },

  computed: {},

  beforeCreate() {
    let token = localStorage.getItem('auth_token')
    let name = this.$router.currentRoute.name
    if (token && name === 'Home') this.$router.push('/main').catch(()=>{})
  },

  created() {
    let token = localStorage.getItem('auth_token')
    if (token) {
      set_token(token)
    }

    let name = this.$router.currentRoute.name
    if (name === 'Home') {
      this.enable_header = false
      this.enable_footer = true
    } else {
      this.ignore_push_main = false
    }
  },

  methods: {
    from_home() {
      this.ignore_push_main = false
      this.enable_header = true
      this.enable_footer = false
    },
  }
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0;
}

#footer {
  background: #cccccc;
  position: fixed;
  left: 0px;
  bottom: 0px;
  height: 30px;
  width: 100%;
}

pre {
  word-wrap: break-word; /* Internet Explorer 5.5+ поддерживается в IE, Safari, и Firefox 3.1.*/
  margin: 10px;
  text-align: left;
  white-space: pre-line;
}

.bookLink {
  color: #2c3e50;
  text-decoration: none;
  font-size: 1em;
  position: relative;
  transition: all 0.6s;
}

.error_logging {
  color: var(--red);
}

.before {
  display: inline-block;
  height: 100%;
  vertical-align: middle;
}

</style>
