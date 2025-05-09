<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import ListRepos from "@/components/ListRepos.vue";
import CommentFeed from "@/components/CommentFeed.vue";
import GetWorkspace from "@/utils/GetWorkspace";
import GetVersionInfo from "@/utils/GetVersionInfo"
import { ref, onMounted, computed } from "vue";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";

const workspace = ref<Workspace | null>(null);
const cascadeMLVersion = ref<string | null>(null);
const cascadeUIVersion = ref<string | null>(null);

onMounted(async () => {
  loadWorkspaceData();

  const versionInfo = await GetVersionInfo();
  console.log(versionInfo)
  cascadeMLVersion.value = versionInfo?.cascade_ml_version
  cascadeUIVersion.value = versionInfo?.cascade_ui_version
});

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return [workspace.value.name];
});

async function loadWorkspaceData() {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
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
    <div class="main-columns">
      <div style="flex: 1;">
        <Suspense>
          <ListRepos v-if="workspace" :workspace="workspace"/>
          <template #fallback>
            Loading...
          </template>
        </Suspense>
        <div class="version-info">
          <p>Cascade version: {{ cascadeMLVersion }} • UI version: {{ cascadeUIVersion }}</p>
        </div>
      </div>
      <CommentFeed
        v-if="workspace"
        :comments="workspace.comments"
        :pathParts="['workspace', workspace.name]"
        :onCommentSent="loadWorkspaceData"
      />
    </div>
  </div>
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
.welcome {
  font-family: 'Montserrat', serif;
  font-style: normal;
  font-weight: 700;
  font-size: 40px;
  line-height: 49px;
  color: #084C61;
}
.version-info {
  color: #b6b6b6;
  margin-top: 300px;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
}
</style>
