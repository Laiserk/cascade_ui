<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetLine from "@/components/GetLine";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {Line} from "@/models/Line";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRouter, useRoute } from 'vue-router'

const route = useRoute()
const router = useRouter()
const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<Line | null>(null);

function openModel(repoName: string, lineName: string, modelNumString: string) {
  router.push({ name: "model", params: { repoName, lineName, modelNumString } });
}

onMounted(async () => {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
    if (repo.value) {
      const lineObj = await GetLine(repoName.value, lineName.value);
      line.value = new Line(lineObj);
    }
  }
}
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value).concat(lineName.value);
});

const modelHeaders = [
  { title: 'Name', value: 'name' },
  { title: 'Slug', value: 'slug' },
  { title: 'Created', value: 'created_at' },
  { title: 'Saved', value: 'saved_at' },
];

</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="stylesheet" href="src/assets/main.css">
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
        <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
        <div v-if="line && line.models">
          <v-data-table :headers="modelHeaders" :items="line.models" class="mt-4">
            <template #item.name="{ item }">
            <v-btn variant="text" color="primary" @click="openModel(repoName, lineName, item.name)">
              {{ item.name }}
            </v-btn>
          </template>
          </v-data-table>
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
</style>