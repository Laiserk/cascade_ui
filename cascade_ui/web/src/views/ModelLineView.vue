<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import GetRepo from "@/components/GetRepo";
import GetLine from "@/components/GetLine";
import GetWorkspace from "@/components/GetWorkspace";
import { ref, onMounted, computed, watch } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {ModelLine} from "@/models/ModelLine";
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
const line = ref<ModelLine | null>(null);

const selectedFields = ref<string[]>([]);
const applyClicked = ref(false);

const defaultFields = ['name', 'slug', 'created_at', 'saved_at'];

async function fetchLineItems() {
  if (!repoName.value || !lineName.value) return;
  const fields = Array.from(new Set(selectedFields.value));
  const response = await fetch("/v1/line_item_table", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      line_path: { repo: repoName.value, line: lineName.value },
      item_fields: fields,
    }),
  });
  if (response.ok) {
    const items = await response.json();
    if (line.value) {
      const filledItems = items.map((item: Record<string, any>, idx: number) => {
        let existing: Record<string, any> | undefined = undefined;
        if (line.value && Array.isArray(line.value.items)) {
          existing = line.value.items[idx] as Record<string, any>;
        }
        for (const field of defaultFields) {
          if (!(field in item)) {
            if (existing && field in existing) {
              item[field] = existing[field];
            } else {
              item[field] = "";
            }
          }
        }
        return item;
      });
      line.value.items = filledItems;
    }
  }
}

const fieldsOptions = computed(() => {
  return line.value?.item_fields.map(field => field.toString()) || [];
});

const dynamicModelHeaders = computed(() => {
  const baseHeaders = [
    { title: 'Name', value: 'name' },
    { title: 'Slug', value: 'slug' },
    { title: 'Created', value: 'created_at' },
    { title: 'Saved', value: 'saved_at' },
  ];
  const selected = selectedFields.value
    .filter(f => !baseHeaders.some(h => h.value === f))
    .map(f => ({ title: f.charAt(0).toUpperCase() + f.slice(1), value: f }));
  return baseHeaders.concat(selected);
});

function applyFields() {
  applyClicked.value = true;
  fetchLineItems();
}

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
      if (!lineObj.item_fields) {
        lineObj.item_fields = [];
      }
      line.value = new ModelLine(lineObj);
    }
  }
}
);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  return workspace.value.name.split(/[/\\]/).filter(Boolean).concat(repoName.value).concat(lineName.value);
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
    <div>
      <div class="content">
        <v-breadcrumbs :items="breadcrumbs"></v-breadcrumbs>
        <div v-if="line && line.items">
          <div class="mb-4" style="display: flex; align-items: center; gap: 16px;">
            <v-select
              v-model="selectedFields"
              :items="fieldsOptions"
              label="Select fields"
              multiple
              chips
              item-title="."
              item-value="."
              :menu-props="{ closeOnContentClick: false }"
              persistent-hint
              hint="Choose fields to display"
              prepend-icon="mdi-table-column"
            >
              <template #item="{ props }">
                <v-list-item v-bind="props">
                </v-list-item>
              </template>
            </v-select>
            <v-btn color="primary" @click="applyFields">Apply</v-btn>
          </div>
          <v-data-table :headers="dynamicModelHeaders" :items="line.items" class="mt-4">
            <template #item.name="{ item }">
              <v-btn variant="text" style="font-family: Roboto,serif; font-size: 14px; color: #DEB841;" @click="openModel(repoName, lineName, item.name)">
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