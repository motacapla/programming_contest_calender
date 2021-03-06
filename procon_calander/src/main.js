import Vue from 'vue'
import App from './App.vue'
import router from './router'
/* import Firebase */

Vue.config.productionTip = false
/* eslint-disable */

new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
