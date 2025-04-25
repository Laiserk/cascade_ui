<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import ListRepos from "@/components/ListRepos.vue";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed } from "vue";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";

const workspace = ref<Workspace | null>(null);

onMounted(async () => {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
});

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  // Split on both forward and backward slashes for cross-platform compatibility
  return workspace.value.name.split(/[/\\]/).filter(Boolean);
});
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
  <div class="content">
    <Suspense>
      <template #fallback>
        <div class="welcome" style="align-content: center">
          Loading...
        </div>
      </template>
    </Suspense>
    <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
    <div class="welcome">
      Welcome to Cascade!
    </div>
    <Suspense>
      <ListRepos v-if="workspace" :workspace="workspace"/>
      <template #fallback>
        Loading...
      </template>
    </Suspense>
  </div>
  </body>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
}

.welcome {
  font-family: 'Montserrat', serif;
  font-style: normal;
  font-weight: 700;
  font-size: 40px;
  line-height: 49px;
  color: #084C61;
}

</style>
