<script setup lang="ts">
import { computed, ref, watch } from "vue";
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
const loading = ref(false);
const pending = ref(0);

// Columns are cached by identifier so that adding one does not re-read the
// meta of the models already on screen. The invariant is that every cached
// column carries every field in fetchedFields
const columnCache = ref<Record<string, CompareColumn>>({});
const notFoundCache = ref<string[]>([]);
const fetchedFields = ref<string[]>([]);

const columns = computed(() => {
  // Ordering follows the URL rather than the response
  return items.value
    .map(id => columnCache.value[id])
    .filter((column): column is CompareColumn => Boolean(column));
});

const notFound = computed(() => items.value.filter(id => notFoundCache.value.includes(id)));

const availableFields = computed(() => {
  const fields = new Set<string>(selectedFields.value);
  for (const column of columns.value) {
    for (const field of column.available_fields) {
      fields.add(field);
    }
  }
  return Array.from(fields).sort();
});

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

function evictDropped() {
  const kept: Record<string, CompareColumn> = {};
  for (const id of items.value) {
    if (columnCache.value[id]) kept[id] = columnCache.value[id];
  }
  columnCache.value = kept;
  notFoundCache.value = notFoundCache.value.filter(id => items.value.includes(id));
}

async function load() {
  evictDropped();

  const known = (id: string) => Boolean(columnCache.value[id]) || notFoundCache.value.includes(id);
  const missingItems = items.value.filter(id => !known(id));
  const newFields = selectedFields.value.filter(field => !fetchedFields.value.includes(field));
  const cachedItems = items.value.filter(id => Boolean(columnCache.value[id]));

  const requests: Promise<void>[] = [];

  // New columns arrive with every field that is currently selected
  if (missingItems.length) {
    requests.push(
      GetCompareTable(missingItems, selectedFields.value).then(response => {
        for (const column of response.columns) {
          columnCache.value[column.id] = column;
        }
        notFoundCache.value = Array.from(
          new Set(notFoundCache.value.concat(response.not_found))
        );
      })
    );
  }

  // Newly selected fields are backfilled into the columns already cached
  if (newFields.length && cachedItems.length) {
    requests.push(
      GetCompareTable(cachedItems, newFields).then(response => {
        for (const column of response.columns) {
          const cached = columnCache.value[column.id];
          if (cached) {
            cached.meta = { ...cached.meta, ...column.meta };
          }
        }
      })
    );
  }

  if (!requests.length) {
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(selectedFields.value)));
    return;
  }

  pending.value += 1;
  loading.value = true;
  try {
    await Promise.all(requests);
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(selectedFields.value)));
  } finally {
    pending.value -= 1;
    loading.value = pending.value > 0;
  }
}

// Cached columns are never re-read, so an edit on disk needs an explicit reload
async function reload() {
  columnCache.value = {};
  notFoundCache.value = [];
  fetchedFields.value = [];
  await load();
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

function removeAllMissing() {
  updateQuery(
    items.value.filter(item => !notFound.value.includes(item)),
    selectedFields.value
  );
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
    >
      Could not find {{ notFound.length }} of the requested models in this workspace.
      <div class="missing-row">
        <v-btn
          v-for="id in notFound"
          :key="id"
          variant="text"
          size="small"
          @click="onRemove(id)"
        >Remove {{ id }}</v-btn>
      </div>
      <template #append>
        <v-btn variant="text" size="small" @click="removeAllMissing">Remove all missing</v-btn>
      </template>
    </v-alert>

    <div v-if="items.length" class="header-row">
      <span class="text">{{ columns.length }} model(s) in comparison</span>
      <v-btn variant="text" size="small" @click="reload">Reload</v-btn>
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

.missing-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.empty {
  margin-top: 40px;
  color: #555;
}
</style>
