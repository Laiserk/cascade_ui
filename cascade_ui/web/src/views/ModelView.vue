<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/utils/GetRepo";
import GetLine from "@/utils/GetLine";
import GetModel from "@/utils/GetModel";
import GetWorkspace from "@/utils/GetWorkspace";
import LogView from "@/components/LogView.vue";
import EnvTable from "@/components/EnvTable.vue";
import TagsRow from "@/components/TagsRow.vue";
import { ref, onMounted, computed, watch } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {Model} from "@/models/Model";
import {ModelLine} from "@/models/ModelLine";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { ModelPathSpec } from "@/models/PathSpecs";
import { Workspace as WorkspaceClass } from "@/models/Workspace";
import { useRoute, useRouter } from 'vue-router'
import ConfigView from "@/components/ConfigView.vue";
import { openWorkspace, openRepo, openLine } from "@/utils/Open";
import CommentFeed from "@/components/CommentFeed.vue";

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

const modelPath = computed(() => {
  if (repo.value && line.value && model.value) {
    return new ModelPathSpec({
      repo: repo.value.name,
      line: line.value.name,
      num: modelNum.value,
    });
  }
  return null;
});

const tab = ref(0);

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
  const wsName = workspace.value.name;
  return [
    {
      title: wsName,
      to: { name: 'main' }
    },
    {
      title: repoName.value,
      to: { name: 'repo', params: { repoName: repoName.value } }
    },
    {
      title: lineName.value,
      to: { name: 'model_line', params: { repoName: repoName.value, lineName: lineName.value } }
    },
    {
      title: modelNumString.value,
      disabled: true
    }
  ];
});

function onBreadcrumbClick(e: any) {
  const item = e?.item;
  if (!item || item.disabled) return;
  if (item.to?.name === 'main') {
    openWorkspace(router);
  } else if (item.to?.name === 'repo') {
    openRepo(router, repoName.value);
  } else if (item.to?.name === 'model_line') {
    openLine(router, { repo: repoName.value, line: lineName.value, lineType: "model_line" });
  }
}

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

// Copy to clipboard logic
const copyFeedback = ref("");
function copySlug() {
  if (model.value?.slug) {
    navigator.clipboard.writeText(model.value.slug);
    copyFeedback.value = "Copied";
    setTimeout(() => {
      copyFeedback.value = "";
    }, 1200);
  }
}

// Add copy for path
const copyPathFeedback = ref("");
function copyPath() {
  if (model.value?.path) {
    navigator.clipboard.writeText(model.value.path);
    copyPathFeedback.value = "Copied!";
    setTimeout(() => {
      copyPathFeedback.value = "";
    }, 1200);
  }
}

// --- Add composable for compare buffer ---
function useCompareBuffer() {
  const KEY = "cascade_compare_models";
  const buffer = ref<string[]>([]);

  function load() {
    const raw = localStorage.getItem(KEY);
    buffer.value = raw ? JSON.parse(raw) : [];
  }
  function save() {
    localStorage.setItem(KEY, JSON.stringify(buffer.value));
  }
  function add(path: string) {
    load();
    if (buffer.value.includes(path)) return;
    if (buffer.value.length < 2) {
      buffer.value.push(path);
    } else {
      buffer.value = [buffer.value[1], path];
    }
    save();
  }
  function remove(path: string) {
    load();
    buffer.value = buffer.value.filter(p => p !== path);
    save();
  }
  function clear() {
    buffer.value = [];
    save();
  }
  load();
  return { buffer, add, remove, clear, load, save };
}

const compareBuffer = useCompareBuffer();

const modelComparePath = computed(() => model.value?.path || "");
</script>

<template>
  <div>
    <NavBar/>
    <div>
      <div class="content">
        <v-breadcrumbs :items="breadcrumbs" @click:item="onBreadcrumbClick"></v-breadcrumbs>
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
          <div class="tabs-column">
            <v-tabs v-model="tab" class="custom-tabs">
              <v-tab class="custom-tab">General</v-tab>
              <v-tab class="custom-tab">Logs</v-tab>
              <v-tab class="custom-tab">Config</v-tab>
            </v-tabs>
            <v-tabs-items v-model="tab">
              <v-tab-item>
                <div v-if="tab === 0" class="general-tab-flex">
                  <div class="model-info">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <p class="slug" style="margin: 0;">{{ model?.slug }}</p>
                      <button
                        v-if="model?.slug"
                        @click="copySlug"
                        title="Copy slug"
                        class="copy-btn"
                        style="background: none; border: none; cursor: pointer; padding: 0;"
                      >
                        <img
                          src="@/assets/copy-icon.png"
                          alt="Copy"
                          style="width: 18px; height: 18px; display: block;"
                        />
                      </button>
                      <span
                        v-if="copyFeedback || true"
                        class="copy-feedback"
                        :class="{ visible: copyFeedback }"
                      >{{ copyFeedback }}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <p class="text" style="margin: 0;">{{ model?.path }}</p>
                      <button
                        v-if="model?.path"
                        @click="copyPath"
                        title="Copy path"
                        class="copy-btn"
                        style="background: none; border: none; cursor: pointer; padding: 0;"
                      >
                        <img
                          src="@/assets/copy-icon.png"
                          alt="Copy"
                          style="width: 18px; height: 18px; display: block;"
                        />
                      </button>
                      <span
                        v-if="copyPathFeedback || true"
                        class="copy-feedback"
                        :class="{ visible: copyPathFeedback }"
                      >{{ copyPathFeedback }}</span>
                    </div>
                    <TagsRow v-if="model" :tags="model.tags"/>
                    <p class="text"> Created: {{ model?.created_at }}</p>
                    <p class="text"> Saved: {{ model?.saved_at }}</p>
                    <div style="margin-top: 20px;margin-bottom: 20px">
                      <p class="text"> {{ model?.description }}</p>
                    </div>

                    <!-- Compare button group START -->
                    <div style="margin-bottom: 16px;">
                      <div style="display: flex; align-items: center; gap: 8px;">
                        <!-- Button for slot 1 -->
                        <v-btn
                          v-if="modelComparePath"
                          :disabled="compareBuffer.buffer.value[0] !== undefined && compareBuffer.buffer.value[0] !== modelComparePath"
                          :style="{
                            minWidth: '40px',
                            marginBottom: '8px',
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            background: (compareBuffer.buffer.value[0] !== undefined && compareBuffer.buffer.value[0] !== modelComparePath)
                              ? '#ccc'
                              : (compareBuffer.buffer.value[0] === modelComparePath ? '#DEB841' : '#E8D496'),
                            color: '#fff',
                            border: 'none',
                            opacity: compareBuffer.buffer.value[0] !== undefined && compareBuffer.buffer.value[0] !== modelComparePath ? 0.5 : 1
                          }"
                          variant="outlined"
                          @click="
                            compareBuffer.buffer.value[0] === modelComparePath
                              ? compareBuffer.remove(modelComparePath)
                              : (
                                  compareBuffer.buffer.value[0] === undefined
                                    ? (compareBuffer.buffer.value[0] = modelComparePath, compareBuffer.save())
                                    : null
                                )
                          "
                        >
                          1
                        </v-btn>
                        <!-- Arrow -->
                        <span style="font-size: 22px; color: #888;">&#8594;</span>
                        <!-- Button for slot 2 -->
                        <v-btn
                          v-if="modelComparePath"
                          :disabled="compareBuffer.buffer.value[1] !== undefined && compareBuffer.buffer.value[1] !== modelComparePath"
                          :style="{
                            minWidth: '40px',
                            marginBottom: '8px',
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            background: (compareBuffer.buffer.value[1] !== undefined && compareBuffer.buffer.value[1] !== modelComparePath)
                              ? '#ccc'
                              : (compareBuffer.buffer.value[1] === modelComparePath ? '#DEB841' : '#E8D496'),
                            color: '#fff',
                            border: 'none',
                            opacity: compareBuffer.buffer.value[1] !== undefined && compareBuffer.buffer.value[1] !== modelComparePath ? 0.5 : 1
                          }"
                          variant="outlined"
                          @click="
                            compareBuffer.buffer.value[1] === modelComparePath
                              ? compareBuffer.remove(modelComparePath)
                              : (
                                  compareBuffer.buffer.value[1] === undefined
                                    ? (compareBuffer.buffer.value[1] = modelComparePath, compareBuffer.save())
                                    : null
                                )
                          "
                        >
                          2
                        </v-btn>
                        <!-- Compare main button -->
                        <v-btn
                          color="primary"
                          :disabled="!(compareBuffer.buffer.value[0] && compareBuffer.buffer.value[1])"
                          style="margin-left: 16px; background: #DEB841; color: #fff; font-weight: bold;"
                        >
                          Compare
                        </v-btn>
                        <!-- Show buffer state for clarity (optional, can remove) -->
                        <span v-if="compareBuffer.buffer.value.length > 0" style="margin-left: 12px; color: #888;">
                          <span v-for="(p, idx) in compareBuffer.buffer.value" :key="String(p)" style="margin-right: 8px;">
                            <code>{{ idx + 1 }}: {{ p }}</code>
                          </span>
                        </span>
                      </div>
                    </div>
                    <!-- Compare button group END -->

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
                        <tr v-for="artifact in model.artifacts" :key="artifact.name">
                          <td>{{ artifact.name }}</td>
                        </tr>
                      </tbody>
                    </v-table>
                    <div v-else style="height:24px"></div>

                    <v-subheader style="margin-top: 32px;">FILES</v-subheader>
                    <v-table v-if="model && model.files && model.files.length">
                      <tbody>
                        <tr v-for="file in model.files" :key="file.name">
                          <td>{{ file.name }}</td>
                          <td>{{ file.size }}</td>
                        </tr>
                      </tbody>
                    </v-table>
                    <div v-else style="height:24px"></div>
                    <EnvTable v-if="model" :tr="model"/>
                  </div>
                  <CommentFeed
                    v-if="model"
                    :comments="model.comments"
                    :pathParts="[repoName, lineName, modelNumString]"
                    :onCommentSent="loadModelData"
                  />
                </div>
              </v-tab-item>
              <v-tab-item>
                <div v-if="tab === 1">
                  <LogView v-if="modelPath" :path="modelPath" />
                </div>
              </v-tab-item>
              <v-tab-item>
                <div v-if="tab === 2">
                  <ConfigView v-if="modelPath" :path="modelPath" />
                </div>
              </v-tab-item>
            </v-tabs-items>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
  max-width: 1600px;
}
.main-columns {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
}
.model-list-column {
  width: 10%;
  min-width: 120px;
  margin-top: 20px;
  margin-right: 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.tabs-column {
  flex: 1;
  margin-top: 20px;
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
  max-height: 1000px;
  overflow-y: auto;
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
.general-tab-flex {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 100%;
}
.model-info {
  margin-top: 20px;
  flex: 0 1 70%;
  min-width: 0;
  margin-left: 0;
  margin-right: 0;
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
.copy-btn {
  font-size: 18px;
  vertical-align: middle;
}
.copy-feedback {
  font-size: 18px;
  color: #db504a77;
  margin-left: 4px;
  opacity: 0;
  transition: opacity 0.35s;
  min-width: 60px;
  display: inline-block;
  font-family: Roboto;
  font-weight: bold;
}
.copy-feedback.visible {
  opacity: 1;
}
.custom-tabs {
  background-color: #F5E6B2;
  border-radius: 8px;
}

.custom-tab {
  color: #DEB841 !important;
  background-color: #FFFDF5 !important;
  transition: background 0.2s, color 0.2s;
}

.custom-tab.v-tab--active,
.custom-tab:hover {
  background-color: #E8D496 !important;
  color: #fff !important;
}
</style>