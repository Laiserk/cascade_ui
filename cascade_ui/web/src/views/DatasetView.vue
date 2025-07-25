<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/utils/GetRepo";
import GetLine from "@/utils/GetLine";
import GetDataset from "@/utils/GetDataset";
import GetWorkspace from "@/utils/GetWorkspace";
import { ref, onMounted, computed, watch } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {Dataset} from "@/models/Dataset";
import {DataLine} from "@/models/DataLine";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute, useRouter } from 'vue-router'
import { openWorkspace, openRepo, openLine } from "@/utils/Open";
import CommentFeed from "@/components/CommentFeed.vue";

const route = useRoute()
const router = useRouter()
const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)
const datasetVer = computed(() => route.params.datasetVer as string)

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<DataLine | null>(null);
const dataset = ref<Dataset | null>(null);

async function loadDatasetData() {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
    if (repo.value) {
      const lineObj = await GetLine(repoName.value, lineName.value);
      line.value = new DataLine(lineObj);
      if (line.value) {
        const datasetObj = await GetDataset(repoName.value, lineName.value, datasetVer.value);
        dataset.value = new Dataset(datasetObj);
      }
    }
  }
}

onMounted(loadDatasetData);

watch(
  [repoName, lineName, datasetVer],
  () => {
    loadDatasetData();
  }
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  const wsName = workspace.value.name;
  return [
    {
      title: wsName,
      to: { name: 'main' }
    },
    {
      title: repoName.value,
      to: { name: 'repo', params: { repoName: repoName.value } }
    },
    {
      title: lineName.value,
      to: { name: 'data_line', params: { repoName: repoName.value, lineName: lineName.value } }
    },
    {
      title: datasetVer.value,
      disabled: true
    }
  ];
});

function onBreadcrumbClick(e: any) {
  const item = e?.item;
  if (!item || item.disabled) return;
  if (item.to?.name === 'main') {
    openWorkspace(router);
  } else if (item.to?.name === 'repo') {
    openRepo(router, repoName.value);
  } else if (item.to?.name === 'data_line') {
    openLine(router, { repo: repoName.value, line: lineName.value, lineType: "data_line" });
  }
}

function goToDataset(datasetVer: string) {
  router.push({
    name: "dataset",
    params: {
      repoName: repoName.value,
      lineName: lineName.value,
      datasetVer: datasetVer
    }
  });
}
</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="icon" href="/logo.svg">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap"
          rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap"
        rel="stylesheet">
  </head>

  <body>
    <NavBar/>
    <div>
      <div class="content">
        <v-breadcrumbs :items="breadcrumbs" @click:item="onBreadcrumbClick"></v-breadcrumbs>
        <div class="main-columns">
          <div class="dataset-list-column">
            <div class="dataset-list-header">Datasets</div>
            <div v-if="line?.items && line.items.length" class="dataset-list">
              <div
                v-for="(m, idx) in line.items"
                :key="idx"
                class="dataset-list-item"
                :class="{ active: m.name === datasetVer }"
                @click="goToDataset(m.name)"
              >
                {{ m.name }}
              </div>
            </div>
          </div>
          <div class="dataset-info">
            <p class="slug"> {{ dataset?.name }}</p>
            <p class="text"> {{ dataset?.path }}</p>
            <div class="tags-row" v-if="dataset?.tags && dataset.tags.length">
              <v-chip
                v-for="tag in dataset.tags"
                :key="tag"
                class="tag-chip"
                :style="{ height: '20px', 'font-size': '13px', 'margin-right': '8px', 'margin-bottom': '8px' }"
                background="#D9D7DD"
                text-color="#555"
                outlined
              >
                {{ tag }}
              </v-chip>
            </div>
            <p class="text"> Saved: {{ dataset?.saved_at }}</p>
            <div style="margin-top: 20px">
              <p class="text"> {{ dataset?.description }}</p>
            </div>
            <EnvTable v-if="dataset" :tr="dataset"/>
          </div>
          <CommentFeed
            v-if="dataset"
            :comments="dataset.comments"
            :pathParts="[repoName, lineName, datasetVer]"
            :onCommentSent="loadDatasetData"
          />
        </div>
      </div>
    </div>
  </body>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
}
.main-columns {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
}
.dataset-list-column {
  width: 10%;
  min-width: 120px;
  margin-top: 20px;
  margin-right: 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.dataset-list-header {
  font-family: Roboto;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 12px;
  color: #333;
}
.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 1000px;
  overflow-y: auto;
}
.dataset-list-item {
  padding: 8px 12px;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  font-family: Roboto;
  font-size: 16px;
  color: #555;
  transition: background 0.2s, color 0.2s;
}
.dataset-list-item.active, .dataset-list-item:hover {
  background: #D9D7DD;
  color: #555;
}
.dataset-info {
  margin-top: 20px;
  flex: 0 1 70%;
  min-width: 0;
  margin-left: 0;
  margin-right: 0;
}
.slug {
  font-family: Roboto;
  font-weight: bold;
  font-size: 24px;
  color: #DB504A;
}
.text {
  font-family: Roboto;
  font-size: 18px;
  color: #898989;
}
.tags-row {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}
.tag-chip {
  padding: 0 10px;
  border-radius: 10px;
  align-items: center;
  display: flex;
}
</style>