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
  </div>
</template>