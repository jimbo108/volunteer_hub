import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import NotFound from '@/components/NotFound'
import Login from '@/components/Login'

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
    path: '/login',
    name: 'Login',
    component: Login
  }
]

export default new Router({
  routes,
  mode: 'history'
})
