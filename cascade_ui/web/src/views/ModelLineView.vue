<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/utils/GetRepo";
import GetLine from "@/utils/GetLine";
import GetWorkspace from "@/utils/GetWorkspace";
import ListItems from "@/components/ListItems.vue";
import CommentFeed from "@/components/CommentFeed.vue";
import PlotsView from "@/components/PlotsView.vue";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {ModelLine} from "@/models/ModelLine";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute, useRouter } from 'vue-router';
import { openWorkspace, openRepo } from "@/utils/Open";
import { LinePathSpec } from "@/models/PathSpecs";

const route = useRoute();
const router = useRouter();
const repoName = computed(() => route.params.repoName as string);
const lineName = computed(() => route.params.lineName as string);

const linePath = computed(() => {
  if (repo.value && line.value) {
    return new LinePathSpec({
      repo: repo.value.name,
      line: line.value.name,
      lineType: line.value.type,
    });
  }
  return null;
});

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<ModelLine | null>(null);
const tab = ref(0);

async function loadLineData() {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
    if (repo.value) {
      const lineObj = await GetLine(repoName.value, lineName.value);
      if (!lineObj.item_fields) {
        lineObj.item_fields = [];
      }
      line.value = new ModelLine(lineObj);
    }
  }
}

onMounted(loadLineData);

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
      disabled: true
    }
  ];
});

function onBreadcrumbClick(e: any) {
  const item = e?.item;
  if (!item || item.disabled) return;
  if (item.to?.name === 'main') {
    openWorkspace(router || ({} as any));
  } else if (item.to?.name === 'repo') {
    openRepo(router || ({} as any), repoName.value);
  }
}
</script>

<template>
  <div>
    <NavBar/>
    <div class="content">
      <v-breadcrumbs :items="breadcrumbs" @click:item="onBreadcrumbClick"></v-breadcrumbs>
      <v-tabs v-model="tab" class="custom-tabs" grow>
        <v-tab class="custom-tab">General</v-tab>
        <v-tab class="custom-tab">Comments</v-tab>
        <v-tab class="custom-tab">Plots</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <div v-if="tab === 0">
            <ListItems v-if="line" :line="line"/>
          </div>
        </v-tab-item>
        <v-tab-item>
          <div v-if="tab === 1">
            <CommentFeed
              v-if="line"
              :comments="line.comments"
              :pathParts="[repoName, lineName]"
              :onCommentSent="loadLineData"
            />
          </div>
        </v-tab-item>
        <v-tab-item>
          <div v-if="tab === 2">
            <PlotsView
              v-if="line && linePath"
              :line="line"
              :linePath="linePath"
            />
          </div>
        </v-tab-item>
      </v-tabs-items>
    </div>
  </div>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
}

.custom-tabs {
  background-color: #F5E6B2;
  border-radius: 8px;
}

.custom-tab {
  color: #DEB841 !important;
  background-color: #FFFDF5 !important;
  transition: background 0.2s, color 0.2s;
}

.custom-tab.v-tab--active,
.custom-tab:hover {
  background-color: #E8D496 !important;
  color: #fff !important;
}
</style>