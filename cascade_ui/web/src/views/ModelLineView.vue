<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetLine from "@/components/GetLine";
import GetWorkspace from "@/components/GetWorkspace";
import ListItems from "@/components/ListItems.vue";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {ModelLine} from "@/models/ModelLine";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute, useRouter } from 'vue-router';
import { openWorkspace, openRepo } from "@/components/Open";

const route = useRoute();
const router = useRouter();
const repoName = computed(() => route.params.repoName as string);
const lineName = computed(() => route.params.lineName as string);

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<ModelLine | null>(null);

onMounted(async () => {
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
});

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
  <NavBar/>
  <div>
    <div class="content">
      <v-breadcrumbs :items="breadcrumbs" @click:item="onBreadcrumbClick"></v-breadcrumbs>
      <ListItems v-if="line" :line="line"/>
    </div>
  </div>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
}
</style>