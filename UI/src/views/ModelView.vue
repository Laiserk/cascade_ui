<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetLine from "@/components/GetLine";
import GetModel from "@/components/GetModel";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {Model} from "@/models/Model";
import {Line} from "@/models/Line";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute } from 'vue-router'

const route = useRoute()
const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)
const modelNumString = computed(() => route.params.modelNumString as string)
const modelNum = computed(() => Number(modelNumString.value));

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<Line | null>(null);
const model = ref<Model | null>(null);


onMounted(async () => {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
    if (repo.value) {
      const lineObj = await GetLine(repoName.value, lineName.value);
      line.value = new Line(lineObj);
      if (line.value) {
        const modelObj = await GetModel(repoName.value, lineName.value, modelNum.value);
        model.value = new Model(modelObj);
      }
    }
  }
}
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value).concat(lineName.value).concat(modelNumString.value);
});

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
        <div class="model-info">
          <p class="slug"> {{ model?.slug }}</p>
          <p class="text"> {{ model?.path }}</p>
          <div class="tags-row" v-if="model?.tags && model.tags.length">
            <v-chip
              v-for="tag in model.tags"
              :key="tag"
              class="tag-chip"
              :style="{ height: '20px', 'font-size': '13px', 'margin-right': '8px', 'margin-bottom': '8px' }"
              color="#898989"
              text-color="#000000"
              outlined
            >
              {{ tag }}
            </v-chip>
          </div>
          <p class="text"> Created: {{ model?.created_at }}</p>
          <p class="text"> Saved: {{ model?.saved_at }}</p>
          <div style="margin-top: 20px">
            <p class="text"> {{ model?.description }}</p>
          </div>
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
.model-info {
  margin-top: 20px;
}
.slug {
  font-family: Roboto;
  font-weight: bold;
  font-size: 24px;
  color: #DB504A;
}
.text {
  font-family: Roboto;
  font-size: 18px;
  color: #898989;
}
.tags-row {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}
.tag-chip {
  padding: 0 10px;
  border-radius: 10px;
  align-items: center;
  display: flex;
}
</style>