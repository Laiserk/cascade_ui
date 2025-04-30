import {createRouter, createWebHistory} from 'vue-router'
import WorkspaceView from '../views/WorkspaceView.vue'
import RepoView from '../views/RepoView.vue'
import ModelLineView from '../views/ModelLineView.vue'
import DataLineView from '../views/DataLineView.vue'
import ModelView from '../views/ModelView.vue'
import DatasetView from '../views/DatasetView.vue'

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
      name: 'model_line',
      component: ModelLineView
    },
    {
      path: '/repos/:repoName/:lineName',
      name: 'data_line',
      component: DataLineView
    },
    {
      path: '/repos/:repoName/:lineName/:modelNumString',
      name: 'model',
      component: ModelView
    },
    {
      path: '/repos/:repoName/:lineName/:datasetVer',
      name: 'dataset',
      component: DatasetView
    },
  ]
})

export default router
