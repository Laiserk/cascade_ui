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

const route = useRoute()
const repoName = route.params.repoName

// onMounted(async () => {
//     if (workspace.value != null) {
//         const wsObj = await GetRepo(repoName);
//         repo.value = wsObj ? new RepoClass(wsObj) : null;
//     }
// });

const repo = ref<Repo | null>(null);

</script>

<template>
    <head>
      <meta charset="utf-8"/>
      <title>repoName</title>
      <p>route.params</p>
      <!-- <link rel="stylesheet" href="src/assets/main.css"> -->
    </head>
    <body>
    <NavBar/>
    </body>
  </template>