import {createRouter, createWebHistory} from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'
import RepoView from '../views/RepoView.vue'
import LineView from '../views/LineView.vue'
import ModelView from '../views/ModelView.vue'

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
    {
      path: '/repos/:repoName/:lineName/:modelNumString',
      name: 'model',
      component: ModelView
    },
  ]
})

export default router
