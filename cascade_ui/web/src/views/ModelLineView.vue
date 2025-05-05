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
import { useRoute } from 'vue-router'

const route = useRoute()
const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)

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
}
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value).concat(lineName.value);
});

</script>

<template>
  <NavBar/>
  <div>
    <div class="content">
      <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
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