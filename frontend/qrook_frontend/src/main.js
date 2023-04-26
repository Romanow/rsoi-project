import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';

import Vue from 'vue';
import App from './App';
import router from './router';
import {store} from './store';

Vue.use(BootstrapVue);

import CountryFlag from 'vue-country-flag'
Vue.component('vue-country-flag', CountryFlag)

import VirtualCollection from 'vue-virtual-collection'
Vue.use(VirtualCollection)

Vue.config.productionTip = false;
new Vue({
  el: '#app',
  store,
  router,
  components: {App},
  template: '<App/>',
});
