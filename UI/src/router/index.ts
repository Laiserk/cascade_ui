import {createRouter, createWebHistory} from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'
import RepoView from '../views/RepoView.vue'
import LineView from '../views/LineView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: WorkspaceView
    },
    {
        path: '/repos/:repoName',
        name: 'repo',
        component: RepoView
    },
    {
      path: '/repos/:repoName/:lineName',
      name: 'line',
      component: LineView
    },
  ]
})

export default router
