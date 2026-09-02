import Vue from 'vue'
import VueRouter from 'vue-router'
import Index from '../views/index'
import List from '../views/list'
import ItemOption from '../views/itemoption'
import EventLog from '../views/eventlog'
import MyInfo from '../views/myinfo'
import addItem from '../views/additem'
import Updata from '../views/updata'
import Login from '../views/Login'
Vue.use(VueRouter);

const routes = [
  {
    path: '/Main',
    name: 'Index',
    component: Index,
    show: true,
    children:[
          {
              path: '/Main/list',
              name: '文物列表',
              component: List
          },
          {
              path: '/Main/myinfo',
              name: '我的信息',
              component: MyInfo
          },
          {
              path: '/Main/eventlog',
              name: '事务管理',
              component: EventLog
          },
          {
              path: '/Main/ItemOption',
              name: '文物操作',
              component: ItemOption
          },
        {
            path: '/Main/additem',
            name: '文物添加',
            component: addItem
        },
        {
            path: '/Main/updata',
            name: '文物更新',
            component: Updata,
            show:false
        }
      ]
  },{
        path: '/',
        name: 'Login',
        component: Login,
        show: true,
    }
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
});

export default router
