import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ReposeView from '../views/ReposeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/main',
      name: 'home',
      component: HomeView
    },
    {
      path: '/repos',
      name: 'repos',
      component: ReposeView
    },
    {
      path: '/data_base',
      name: 'data_base',
      component: HomeView
    }
  ]
})

export default router
