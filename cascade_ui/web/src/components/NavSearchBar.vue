<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useDebounceFn } from "@vueuse/core";
import {
  mdiCube,
  mdiDatabase,
  mdiChartTimelineVariant,
  mdiMagnify,
  mdiSourceRepository,
  mdiTable,
} from "@mdi/js";
import GetNavSuggestions from "@/utils/GetNavSuggestions";
import type { Type, NavSuggestion } from "@/models/Nav";
import { isExactMatch, navRoute, navSubtitle } from "@/models/Nav";

const LIMIT = 50;

const SEARCH_TIP =
  "Jump to a model by slug, or to any repo, line, model or dataset" +
  " by path like 00000/00003";

const KIND_ICONS: Record<Type, string> = {
  repo: mdiSourceRepository,
  model_line: mdiChartTimelineVariant,
  data_line: mdiTable,
  model: mdiCube,
  dataset: mdiDatabase,
};

const router = useRouter();

const search = ref("");
const selected = ref<NavSuggestion | null>(null);
const suggestions = ref<NavSuggestion[]>([]);
const total = ref(0);
const loading = ref(false);

const isEmptyQuery = computed(() => !search.value?.trim());

const hint = computed(() =>
  total.value > suggestions.value.length
    ? `Showing ${suggestions.value.length} of ${total.value} matches,`
      + " keep typing to narrow it down"
    : SEARCH_TIP
);

let latestRequest = 0;
let navigating = false;

async function request(query: string) {
  const requestId = ++latestRequest;
  loading.value = true;
  const response = await GetNavSuggestions(query, LIMIT);
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

function navigate(item: NavSuggestion) {
  navigating = true;
  router.push(navRoute(item));
}

function onSelect(item: NavSuggestion | null) {
  if (!item) return;
  navigate(item);
}


async function onEnter() {
  if (navigating || selected.value) return;
  const query = search.value?.trim();
  if (!query) return;

  await request(query);
  const top = suggestions.value[0];
  if (top && isExactMatch(query, top)) {
    navigate(top);
  }
}
</script>

<template>
  <div class="nav-search">
    <v-autocomplete
      v-model="selected"
      :items="suggestions"
      :loading="loading"
      :search="search"
      :prepend-inner-icon="mdiMagnify"
      :hint="hint"
      label="Search"
      item-title="path"
      return-object
      no-filter
      hide-selected
      persistent-hint
      clearable
      variant="solo"
      density="comfortable"
      @update:search="onSearch"
      @update:model-value="onSelect"
      @keydown.enter="onEnter"
    >
      <template #item="{ props, item }">
        <v-list-item
          v-bind="props"
          :title="item.raw.path"
          :subtitle="navSubtitle(item.raw)"
          :prepend-icon="KIND_ICONS[item.raw.type as Type]"
        />
      </template>
      <template #no-data>
        <v-list-item
          :title="isEmptyQuery ? SEARCH_TIP : 'Nothing matches this query'"
          :class="{ 'nav-search-tip': isEmptyQuery }"
        />
      </template>
    </v-autocomplete>
  </div>
</template>

<style scoped>
.nav-search {
  width: 100%;
  max-width: 720px;
  margin: 56px auto 32px auto;
}
.nav-search-tip :deep(.v-list-item-title) {
  white-space: normal;
  font-size: 0.875rem;
  opacity: 0.7;
}
</style>
