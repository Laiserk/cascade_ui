<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";

import { useRouter, useRoute } from 'vue-router'

const workspace = ref<Workspace | null>(null);

const route = useRoute()
const repoName = computed(() => route.params.repoName as string)

const repo = ref<Repo | null>(null);
const router = useRouter();

function openLine(repoName: string, lineName: string, lineType: string) {
  if (lineType === "model_line") {
    router.push({ name: "model_line", params: { repoName, lineName } });
  }
  else if (lineType === "data_line") {
    router.push({ name: "data_line", params: { repoName, lineName } });
  }
  else {
    throw Error()
  }
}

onMounted(async () => {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
  }
});

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value);
});

const lineHeaders = [
  { title: 'Name', value: 'name' },
  { title: 'Type', value: 'type' },
  { title: 'Len', value: 'len' },
  { title: 'Tags', value: 'tags' },
  { title: 'Created', value: 'created_at' },
  { title: 'Updated', value: 'updated_at' },
];

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
    <div>
    <NavBar/>
    <div class="content">
      <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
      <div v-if="repo && repo.lines">
        <v-data-table :headers="lineHeaders" :items="repo.lines" class="mt-4">
          <template #item.name="{ item }">
            <v-btn variant="text" style="font-family: Roboto,serif; font-size: 14px; color: #DEB841;" @click="openLine(repoName, item.name, item.type)">
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