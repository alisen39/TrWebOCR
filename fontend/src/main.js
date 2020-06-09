import Vue from 'vue'
import App from './App.vue'
import router from './router'
import {
  Button,
  Layout,
  Input,
  Row,
  Col,
  Icon,
  Divider,
  Upload,

} from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css';
import axios from 'axios'
import VueHighlightJS from 'vue-highlightjs'
Vue.use(VueHighlightJS)


Vue.use(Button)
Vue.use(Layout)
Vue.use(Input)
Vue.use(Row)
Vue.use(Col)
Vue.use(Icon)
Vue.use(Divider)
Vue.use(Upload)



Vue.config.productionTip = false

axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
axios.defaults.headers.get['Content-Type'] = 'application/x-www-form-urlencoded';
axios.defaults.transformRequest = [function (data) {
  let ret = ''
  for (let it in data) {
    ret += encodeURIComponent(it) + '=' + encodeURIComponent(data[it]) + '&'
  }
  return ret
}]

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')