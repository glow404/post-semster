import { createApp } from 'vue'
import App from './App.vue'

import axios from 'axios'
import VueAxios from 'vue-axios'
import $ from 'jquery'

import router from './router/index'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import * as ElIconModules from '@element-plus/icons-vue'

import GRouter from './router/routes'
import global from './assets/global.js'

import './assets/me.css'


const app = createApp(App)

const userInfo = JSON.parse(localStorage.getItem('userInfo'));

if (userInfo != null && userInfo != undefined) {
    axios.defaults.headers['Authorization'] = userInfo.token;
}
axios.defaults.headers['ip'] = sessionStorage.getItem('ip');    //这几行代码从本地存储中获取用户信息，并将用户的 token 设置为 axios 请求的默认请求头。另外，将从会话存储中获取的 IP 地址设置为 axios 请求的默认请求头。

app.use(ElementPlus)
app.use(VueAxios, axios)
app.use(router)
app.use($)

app.config.silent = true
app.config.productionTip = false

axios.defaults.baseURL = 'http://localhost:8080/'
    //axios.defaults.baseURL = 'http://4e4v608110.qicp.vip:33277/'

// 统一注册Icon图标
for (const iconName in ElIconModules) {
    if (Reflect.has(ElIconModules, iconName)) {
        const item = ElIconModules[iconName]
        app.component(iconName, item)
    }
}

app.config.globalProperties.$GRouter = GRouter;
app.config.globalProperties.global = global;

app.mount('#app')