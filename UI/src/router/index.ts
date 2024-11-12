import {createRouter, createWebHistory} from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'
import ReposeView from '../views/ReposeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: WorkspaceView
    },
    {
      path: '/repos',
      name: 'repos',
      component: ReposeView
    },
    {
      path: '/data_base',
      name: 'data_base',
      component: WorkspaceView
    }
  ]
})

export default router
