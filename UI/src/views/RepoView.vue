<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";

import { useRoute } from 'vue-router'

const workspace = ref<Workspace | null>(null);

const route = useRoute()
const repoName = computed(() => route.params.repoName as string)

const repo = ref<Repo | null>(null);

onMounted(async () => {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
  }
});

const workspaceName = computed(() => workspace.value?.name ?? '');

// Table headers for lines
const lineHeaders = [
  { title: 'Name', value: 'name' },
  { title: 'Type', value: 'type' },
  { title: 'Created At', value: 'created_at' },
  { title: 'Updated At', value: 'updated_at' },
  { title: 'Len', value: 'len' },
];

</script>

<template>
  <div>
    <NavBar/>
    <div>
      <p>Route param repoName: {{ repoName }}</p>
      <p>Workspace: {{ workspaceName }}</p>
      <p v-if="repo">Repo: {{ repo.name }} ({{ repo.len }} lines)</p>
      <p v-else>Loading repo...</p>
    </div>
    <div v-if="repo && repo.lines">
      <v-data-table :headers="lineHeaders" :items="repo.lines" class="mt-4">
      </v-data-table>
    </div>
  </div>
</template>