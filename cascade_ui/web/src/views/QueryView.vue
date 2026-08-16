<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavBar from "../components/NavBar.vue";
import QueryTable from "@/components/QueryTable.vue";
import RunQuery from "@/utils/RunQuery";
import { DEFAULT_COLUMNS, DEFAULT_LIMIT, toCliCommand } from "@/models/Query";
import type { QueryRequest, QueryResponse } from "@/models/Query";
import {
  mdiArrowDown,
  mdiArrowUp,
  mdiChevronLeft,
  mdiChevronRight,
  mdiContentCopy,
  mdiFilterOutline,
  mdiPlay,
  mdiSort,
  mdiTableColumn
} from "@mdi/js";

const route = useRoute();
const router = useRouter();

// Drafts hold what the user is typing. They only reach the URL on Run,
// every run is a full pass over the workspace and must not fire per keystroke
const columns = ref<string[]>([...DEFAULT_COLUMNS]);
const filterExpr = ref("");
const sortExpr = ref("");
const desc = ref(false);
const filterShown = ref(false);
const sortShown = ref(false);

const result = ref<QueryResponse | null>(null);
const loading = ref(false);
const copied = ref(false);
const ranRequest = ref<QueryRequest | null>(null);

const offset = computed(() => {
  const value = Number(route.query.offset);
  return Number.isInteger(value) && value > 0 ? value : 0;
});

const limit = computed(() => {
  const value = Number(route.query.limit);
  return Number.isInteger(value) && value > 0 ? value : DEFAULT_LIMIT;
});

const hasQuery = computed(() => typeof route.query.columns === "string");

const draftRequest = computed<QueryRequest>(() => ({
  columns: columns.value,
  filter_expr: filterShown.value && filterExpr.value ? filterExpr.value : null,
  sort_expr: sortShown.value && sortExpr.value ? sortExpr.value : null,
  desc: desc.value,
  offset: offset.value,
  limit: limit.value
}));

const cliCommand = computed(() => toCliCommand(draftRequest.value));

const rangeLabel = computed(() => {
  if (!result.value || !result.value.rows.length) return "";
  const first = offset.value + 1;
  return `Rows ${first}–${offset.value + result.value.rows.length}`;
});

function parseColumns(value: unknown): string[] {
  if (typeof value !== "string" || !value) return [...DEFAULT_COLUMNS];
  const parsed = value.split(",").filter(part => part.length > 0);
  return parsed.length ? parsed : [...DEFAULT_COLUMNS];
}

function parseText(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function updateQuery(request: QueryRequest) {
  const query: Record<string, string> = {
    columns: request.columns.join(","),
    offset: String(request.offset),
    limit: String(request.limit)
  };
  if (request.filter_expr) query.filter = request.filter_expr;
  if (request.sort_expr) {
    query.sort = request.sort_expr;
    if (request.desc) query.desc = "1";
  }

  router.push({ name: "query", query: query });
}

function onRun() {
  // A changed query starts over from the first page
  updateQuery({ ...draftRequest.value, offset: 0 });
}

function onPage(direction: number) {
  const next = Math.max(0, offset.value + direction * limit.value);
  updateQuery({ ...draftRequest.value, offset: next });
}

function onAddFilter() {
  filterShown.value = true;
}

function onRemoveFilter() {
  filterShown.value = false;
  filterExpr.value = "";
}

function onAddSort() {
  sortShown.value = true;
}

function onRemoveSort() {
  sortShown.value = false;
  sortExpr.value = "";
  desc.value = false;
}

async function onCopy() {
  try {
    await navigator.clipboard.writeText(cliCommand.value);
    copied.value = true;
    setTimeout(() => (copied.value = false), 1500);
  } catch (error) {
    console.log(error);
  }
}

async function syncFromQuery() {
  if (!hasQuery.value) {
    result.value = null;
    ranRequest.value = null;
    return;
  }

  columns.value = parseColumns(route.query.columns);
  filterExpr.value = parseText(route.query.filter);
  sortExpr.value = parseText(route.query.sort);
  desc.value = route.query.desc === "1";
  filterShown.value = filterShown.value || Boolean(filterExpr.value);
  sortShown.value = sortShown.value || Boolean(sortExpr.value);

  const request = draftRequest.value;
  loading.value = true;
  try {
    result.value = await RunQuery(request);
    ranRequest.value = request;
  } finally {
    loading.value = false;
  }
}

watch(() => route.query, syncFromQuery, { immediate: true });
</script>

<template>
  <NavBar/>
  <div class="content">
    <v-breadcrumbs :items="['Query']"></v-breadcrumbs>

    <div class="expr-row columns-row">
      <v-icon :icon="mdiTableColumn" class="expr-icon"/>
      <v-combobox
        v-model="columns"
        label="Columns"
        hint="Meta field names, for example created_at or metrics[0].value. Press enter to add"
        persistent-hint
        multiple
        chips
        closable-chips
        variant="outlined"
        density="compact"
        @keyup.enter.stop
      />
      <div class="expr-spacer"/>
    </div>

    <div v-if="filterShown" class="expr-row">
      <v-icon :icon="mdiFilterOutline" class="expr-icon"/>
      <v-text-field
        v-model="filterExpr"
        label="filter"
        placeholder="metrics[0].value > 0.8 and 'prod' in tags"
        variant="outlined"
        density="compact"
        hide-details
        @keyup.enter="onRun"
      />
      <v-btn icon variant="text" size="small" @click="onRemoveFilter">
        <v-icon icon="$close"/>
        <v-tooltip activator="parent" location="top">Remove filter</v-tooltip>
      </v-btn>
    </div>

    <div v-if="sortShown" class="expr-row">
      <v-icon :icon="mdiSort" class="expr-icon"/>
      <v-text-field
        v-model="sortExpr"
        label="sort"
        placeholder="created_at"
        variant="outlined"
        density="compact"
        hide-details
        @keyup.enter="onRun"
      />
      <v-btn icon variant="text" size="small" @click="desc = !desc">
        <v-icon :icon="desc ? mdiArrowDown : mdiArrowUp"/>
        <v-tooltip activator="parent" location="top">
          {{ desc ? "Descending" : "Ascending" }}
        </v-tooltip>
      </v-btn>
      <v-btn icon variant="text" size="small" @click="onRemoveSort">
        <v-icon icon="$close"/>
        <v-tooltip activator="parent" location="top">Remove sort</v-tooltip>
      </v-btn>
    </div>

    <div class="action-row">
      <v-btn
        v-if="!filterShown"
        variant="text"
        size="small"
        :prepend-icon="mdiFilterOutline"
        @click="onAddFilter"
      >Add filter</v-btn>
      <v-btn
        v-if="!sortShown"
        variant="text"
        size="small"
        :prepend-icon="mdiSort"
        @click="onAddSort"
      >Add sort</v-btn>
      <v-spacer/>
      <v-btn
        color="#084C61"
        variant="flat"
        :prepend-icon="mdiPlay"
        :disabled="!columns.length"
        @click="onRun"
      >Run</v-btn>
    </div>

    <div class="cli-row">
      <code class="cli-command">{{ cliCommand }}</code>
      <v-btn icon variant="text" size="x-small" @click="onCopy">
        <v-icon :icon="mdiContentCopy" size="18"/>
        <v-tooltip activator="parent" location="top">
          {{ copied ? "Copied" : "Copy as CLI command" }}
        </v-tooltip>
      </v-btn>
    </div>

    <v-progress-linear v-if="loading" indeterminate color="#084C61" class="mt-2"/>

    <v-alert
      v-if="result && result.error"
      type="error"
      variant="tonal"
      class="mt-4"
    >{{ result.error }}</v-alert>

    <template v-if="result && !result.error && ranRequest">
      <div class="header-row">
        <span class="text">{{ rangeLabel || "No rows" }}</span>
        <span class="text time">{{ result.time_s }}s</span>
      </div>

      <QueryTable
        v-if="result.rows.length"
        :columns="ranRequest.columns"
        :rows="result.rows"
        :workspace-root="result.workspace_root"
      />
      <div v-else class="empty">
        Nothing matched. Columns that do not exist in the meta come back empty,
        so check the spelling if every value is a dash.
      </div>

      <div v-if="offset || result.has_next" class="paging-row">
        <v-btn
          variant="text"
          size="small"
          :prepend-icon="mdiChevronLeft"
          :disabled="offset === 0 || loading"
          @click="onPage(-1)"
        >Previous</v-btn>
        <v-btn
          variant="text"
          size="small"
          :append-icon="mdiChevronRight"
          :disabled="!result.has_next || loading"
          @click="onPage(1)"
        >Next</v-btn>
      </div>
    </template>

    <div v-if="!result && !loading" class="empty">
      Query the whole workspace by meta field.
      You can try slug, created_at or nested fields like metrics[0] or params.lr
      Filter and sort take plain Python expressions.
    </div>
  </div>
</template>

<style scoped>
.content {
  margin-left: 60px;
  margin-right: 60px;
}

.expr-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.expr-icon {
  color: #084C61;
}

.columns-row {
  align-items: flex-start;
}

.columns-row .expr-icon {
  margin-top: 8px;
}

.expr-spacer {
  width: 28px;
  flex: none;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.cli-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.cli-command {
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  white-space: nowrap;
  background-color: #F5F5F5;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
  color: #555;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 8px;
}

.time {
  color: #555;
}

.paging-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.empty {
  margin-top: 40px;
  color: #555;
}
</style>
