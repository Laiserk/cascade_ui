<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetLine from "@/components/GetLine";
import GetModel from "@/components/GetModel";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed, watch } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {Model} from "@/models/Model";
import {ModelLine} from "@/models/ModelLine";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)
const modelNumString = computed(() => route.params.modelNumString as string)
const modelNum = computed(() => Number(modelNumString.value));

const workspace = ref<Workspace | null>(null);
const repo = ref<Repo | null>(null);
const line = ref<ModelLine | null>(null);
const model = ref<Model | null>(null);

async function loadModelData() {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
    if (repo.value) {
      const lineObj = await GetLine(repoName.value, lineName.value);
      line.value = new ModelLine(lineObj);
      if (line.value) {
        const modelObj = await GetModel(repoName.value, lineName.value, modelNum.value);
        model.value = new Model(modelObj);
      }
    }
  }
}

onMounted(loadModelData);

watch(
  [repoName, lineName, modelNumString],
  () => {
    loadModelData();
  }
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value).concat(lineName.value).concat(modelNumString.value);
});

function goToModel(modelNumString: string) {
  router.push({
    name: "model",
    params: {
      repoName: repoName.value,
      lineName: lineName.value,
      modelNumString: modelNumString
    }
  });
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

  <body>
    <NavBar/>
    <div>
      <div class="content">
        <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
        <div class="main-columns">
          <div class="model-list-column">
            <div class="model-list-header">Models</div>
            <div v-if="line?.items && line.items.length" class="model-list">
              <div
                v-for="(m, idx) in line.items"
                :key="idx"
                class="model-list-item"
                :class="{ active: m.name === modelNumString }"
                @click="goToModel(m.name)"
              >
                {{ m.name }}
              </div>
            </div>
          </div>
          <div class="model-info">
            <p class="slug"> {{ model?.slug }}</p>
            <p class="text"> {{ model?.path }}</p>
            <div class="tags-row" v-if="model?.tags && model.tags.length">
              <v-chip
                v-for="tag in model.tags"
                :key="tag"
                class="tag-chip"
                :style="{ height: '20px', 'font-size': '13px', 'margin-right': '8px', 'margin-bottom': '8px' }"
                background="#D9D7DD"
                text-color="#555"
                outlined
              >
                {{ tag }}
              </v-chip>
            </div>
            <p class="text"> Created: {{ model?.created_at }}</p>
            <p class="text"> Saved: {{ model?.saved_at }}</p>
            <div style="margin-top: 20px;margin-bottom: 20px">
              <p class="text"> {{ model?.description }}</p>
            </div>

            <v-subheader style="margin-top: 32px;">PARAMETERS</v-subheader>
            <v-table v-if="model && model.params && Object.keys(model.params).length">
              <tbody>
                <tr v-for="(value, key) in model.params" :key="key">
                  <td><b>{{ key }}</b></td>
                  <td>{{ typeof value === 'object' ? JSON.stringify(value) : String(value) }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-else style="height:24px"></div>

            <v-subheader style="margin-top: 32px;">METRICS</v-subheader>
            <v-table v-if="model && model.metrics && model.metrics.length">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Value</th>
                  <th>Dataset</th>
                  <th>Split</th>
                  <th>Direction</th>
                  <th>Interval</th>
                  <th>Extra</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(metric, idx) in model.metrics" :key="idx">
                  <td>{{ metric.name }}</td>
                  <td>{{ metric.value }}</td>
                  <td>{{ metric.dataset }}</td>
                  <td>{{ metric.split }}</td>
                  <td>{{ metric.direction }}</td>
                  <td>
                    <span v-if="metric.interval">
                      [{{ metric.interval[0] }}, {{ metric.interval[1] }}]
                    </span>
                    <span v-else>-</span>
                  </td>
                  <td>
                    <span v-if="metric.extra">{{ JSON.stringify(metric.extra) }}</span>
                    <span v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <div v-else style="height:24px"></div>

            <v-subheader style="margin-top: 32px;">ARTIFACTS</v-subheader>
            <v-table v-if="model && model.artifacts && model.artifacts.length">
              <tbody>
                <tr v-for="artifact in model.artifacts" :key="artifact">
                  <td>{{ artifact }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-else style="height:24px"></div>

            <v-subheader style="margin-top: 32px;">FILES</v-subheader>
            <v-table v-if="model && model.files && model.files.length">
              <tbody>
                <tr v-for="file in model.files" :key="file">
                  <td>{{ file }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-else style="height:24px"></div>

            <div v-if="model && (model.python_version && model.git_commit && model.user && model.host && model.cwd)" style="height:24px">
              <v-subheader style="margin-top: 32px;">ENVIRONMENT</v-subheader>
              <v-table v-if="model">
                <tbody>
                  <tr>
                    <td><b>Python version</b></td>
                    <td>{{ model.python_version }}</td>
                  </tr>
                  <tr>
                    <td><b>Git commit</b></td>
                    <td>{{ model.git_commit }}</td>
                  </tr>
                  <tr>
                    <td><b>Host</b></td>
                    <td>{{ model.user }}@{{ model.host }}</td>
                  </tr>
                  <tr>
                    <td><b>CWD</b></td>
                    <td>{{ model.cwd }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>

          </div>
          <div class="comments-section">
            <div
              v-for="comment in model?.comments"
              :key="comment.id"
              class="comment-bubble"
            >
              <div class="comment-header">
                <span class="comment-user">{{ comment.user }}@{{ comment.host }}</span>
                <span class="comment-timestamp">{{ comment.timestamp }}</span>
              </div>
              <div class="comment-message">
                {{ comment.message }}
              </div>
            </div>
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
.main-columns {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
}
.model-list-column {
  width: 20%;
  min-width: 120px;
  margin-top: 20px;
  margin-right: 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.model-list-header {
  font-family: Roboto;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 12px;
  color: #333;
}
.model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.model-list-item {
  padding: 8px 12px;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  font-family: Roboto;
  font-size: 16px;
  color: #555;
  transition: background 0.2s, color 0.2s;
}
.model-list-item.active, .model-list-item:hover {
  background: #D9D7DD;
  color: #555;
}
.model-info {
  margin-top: 20px;
  width: 60%;
  margin-left: 0;
  margin-right: 0;
}
.comments-section {
  flex: 1;
  margin-top: 20px;
  margin-left: 40px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
.comment-bubble {
  background: #f4f4f4;
  border-radius: 12px;
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 14px;
  color: #888;
}
.comment-user {
  font-weight: bold;
}
.comment-timestamp {
  font-size: 13px;
  color: #aaa;
}
.comment-message {
  font-size: 16px;
  color: #222;
  word-break: break-word;
}
</style>