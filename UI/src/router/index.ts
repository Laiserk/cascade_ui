import {createRouter, createWebHistory} from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: WorkspaceView
    },
  ]
})

export default router
