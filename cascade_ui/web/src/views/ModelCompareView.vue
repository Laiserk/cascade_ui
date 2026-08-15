<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavBar from "../components/NavBar.vue";
import ModelSearchBar from "@/components/ModelSearchBar.vue";
import CompareTable from "@/components/CompareTable.vue";
import GetCompareTable from "@/utils/GetCompareTable";
import { useCompareStore } from "@/utils/CompareStore";
import type { CompareColumn } from "@/models/Compare";

const route = useRoute();
const router = useRouter();
const store = useCompareStore();

const items = ref<string[]>([]);
const selectedFields = ref<string[]>([]);
const columns = ref<CompareColumn[]>([]);
const availableFields = ref<string[]>([]);
const notFound = ref<string[]>([]);
const loading = ref(false);

function parseQuery(value: unknown): string[] {
  if (typeof value !== "string" || !value) return [];
  return value.split(",").filter(part => part.length > 0);
}

function updateQuery(nextItems: string[], nextFields: string[]) {
  const query: Record<string, string> = {};
  if (nextItems.length) query.items = nextItems.join(",");
  if (nextFields.length) query.fields = nextFields.join(",");
  router.replace({ name: "compare", query: query });
}

async function load() {
  if (!items.value.length) {
    columns.value = [];
    availableFields.value = [];
    notFound.value = [];
    return;
  }
  loading.value = true;
  const response = await GetCompareTable(items.value, selectedFields.value);
  columns.value = response.columns;
  availableFields.value = response.item_fields;
  notFound.value = response.not_found;
  loading.value = false;
}

// Staging is only picked up when entering the view. Later on an empty list
// means the user emptied it, and must not be refilled from the store
let hydrated = false;

// The URL is the source of truth, every mutation goes through it
async function syncFromQuery() {
  const queryItems = parseQuery(route.query.items);
  const queryFields = parseQuery(route.query.fields);
  const firstSync = !hydrated;
  hydrated = true;

  if (firstSync && !queryItems.length && store.items.value.length) {
    // Arriving with models staged from model pages - put them into the URL
    // right away so that the comparison becomes shareable
    updateQuery(store.items.value, queryFields);
    return;
  }

  items.value = queryItems;
  selectedFields.value = queryFields;
  store.replaceAll(queryItems);
  await load();
}

watch(() => route.query, syncFromQuery, { immediate: true });

function onSelect(id: string) {
  if (items.value.includes(id)) return;
  updateQuery(items.value.concat([id]), selectedFields.value);
}

function onRemove(id: string) {
  updateQuery(items.value.filter(item => item !== id), selectedFields.value);
}

function onFieldsUpdate(fields: string[]) {
  updateQuery(items.value, fields);
}

function clearAll() {
  updateQuery([], selectedFields.value);
}
</script>

<template>
  <NavBar/>
  <div class="content">
    <v-breadcrumbs :items="['Compare models']"></v-breadcrumbs>

    <ModelSearchBar @select="onSelect"/>

    <v-alert
      v-if="notFound.length"
      type="warning"
      variant="tonal"
      class="mt-4"
      closable
    >
      Could not find {{ notFound.join(", ") }} in this workspace.
      <v-btn
        v-for="id in notFound"
        :key="id"
        variant="text"
        size="small"
        @click="onRemove(id)"
      >Remove {{ id }}</v-btn>
    </v-alert>

    <div v-if="items.length" class="header-row">
      <span class="text">{{ columns.length }} model(s) in comparison</span>
      <v-btn variant="text" size="small" @click="clearAll">Clear all</v-btn>
    </div>

    <v-progress-linear v-if="loading" indeterminate color="#084C61" class="mt-2"/>

    <CompareTable
      v-if="columns.length"
      :columns="columns"
      :item-fields="availableFields"
      :selected-fields="selectedFields"
      @remove="onRemove"
      @update:selected-fields="onFieldsUpdate"
    />

    <div v-else-if="!loading" class="empty">
      Find models by their path like <b>repo/line/model</b>, by its tail like
      <b>00000/00003</b>, or by slug. Selected models appear here as columns.
    </div>
  </div>
</template>

<style scoped>
.content {
  margin-left: 60px;
  margin-right: 60px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.empty {
  margin-top: 40px;
  color: #555;
}
</style>
