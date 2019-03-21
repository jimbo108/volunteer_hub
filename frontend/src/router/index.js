import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import NotFound from '@/components/NotFound'
import RegisterUser from '@/components/RegisterUser'

Vue.use(Router)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound
  },
  {
    path: '/registerUser',
    name: 'RegisterUser',
    component: RegisterUser
  }
]

export default new Router({
  routes,
  mode: 'history'
})
