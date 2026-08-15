<script setup lang="ts">
import { ref } from "vue";
import { useDebounceFn } from "@vueuse/core";
import GetItemSuggestions from "@/utils/GetItemSuggestions";
import type { ItemSuggestion } from "@/models/Compare";
import { itemId } from "@/models/Compare";

const LIMIT = 50;

const emit = defineEmits<{ (e: "select", id: string): void }>();

const search = ref("");
const selected = ref<ItemSuggestion | null>(null);
const suggestions = ref<ItemSuggestion[]>([]);
const total = ref(0);
const loading = ref(false);

let latestRequest = 0;

async function request(query: string) {
  const requestId = ++latestRequest;
  loading.value = true;
  const response = await GetItemSuggestions(query, LIMIT);
  if (requestId !== latestRequest) return;
  suggestions.value = response.items;
  total.value = response.total;
  loading.value = false;
}

const requestDebounced = useDebounceFn(request, 250);

function onSearch(query: string) {
  search.value = query;
  requestDebounced(query || "");
}

function onSelect(item: ItemSuggestion | null) {
  if (!item) return;
  emit("select", itemId(item));
  selected.value = null;
  search.value = "";
  request("");
}

request("");
</script>

<template>
  <v-autocomplete
    v-model="selected"
    :items="suggestions"
    :loading="loading"
    :search="search"
    :hint="total > suggestions.length
      ? `Showing ${suggestions.length} of ${total} matches, keep typing to narrow it down`
      : 'Search by repo/line/model, partial path like 00000/00003, or by model slug'"
    label="Add a model to comparison"
    item-title="path"
    return-object
    no-filter
    hide-selected
    persistent-hint
    clearable
    @update:search="onSearch"
    @update:model-value="onSelect"
  >
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="item.raw.path" :subtitle="item.raw.slug ?? ''"/>
    </template>
    <template #no-data>
      <v-list-item title="No models match this query"/>
    </template>
  </v-autocomplete>
</template>
