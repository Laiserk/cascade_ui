<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavBar from "../components/NavBar.vue";
import LineSearchBar from "@/components/LineSearchBar.vue";
import MetricChart from "@/components/MetricChart.vue";
import GetPlotSeries from "@/utils/GetPlotSeries";
import type { PlotSeries } from "@/models/Plots";
import { seriesColor } from "@/utils/PlotColors";

const route = useRoute();
const router = useRouter();

const lines = ref<string[]>([]);
const metrics = ref<string[]>([]);
const loading = ref(false);
const pending = ref(0);

// Series are cached by identifier so that adding a line does not re-read the
// metas of the lines already on screen. The invariant is that every cached
// series carries every field in fetchedFields
const seriesCache = ref<Record<string, PlotSeries>>({});
const notFoundCache = ref<string[]>([]);
const fetchedFields = ref<string[]>([]);

const series = computed(() => {
  return lines.value
    .map(id => seriesCache.value[id])
    .filter((item): item is PlotSeries => Boolean(item));
});

const notFound = computed(() => lines.value.filter(id => notFoundCache.value.includes(id)));

const plotFields = computed(() => {
  const fields = new Set<string>();
  for (const item of series.value) {
    for (const field of item.plot_fields) {
      fields.add(field);
    }
  }
  return Array.from(fields).sort();
});

// Only one chart for now, but the URL already carries a list of them
const selectedMetric = computed({
  get: () => metrics.value[0] ?? null,
  set: (field: string | null) => updateQuery(lines.value, field ? [field] : [])
});

function parseQuery(value: unknown): string[] {
  if (typeof value !== "string" || !value) return [];
  return value.split(",").filter(part => part.length > 0);
}

function updateQuery(nextLines: string[], nextMetrics: string[]) {
  const query: Record<string, string> = {};
  if (nextLines.length) query.lines = nextLines.join(",");
  if (nextMetrics.length) query.metrics = nextMetrics.join(",");
  router.replace({ name: "plots", query: query });
}

function evictDropped() {
  const kept: Record<string, PlotSeries> = {};
  for (const id of lines.value) {
    if (seriesCache.value[id]) kept[id] = seriesCache.value[id];
  }
  seriesCache.value = kept;
  notFoundCache.value = notFoundCache.value.filter(id => lines.value.includes(id));
}

async function load() {
  evictDropped();

  const known = (id: string) => Boolean(seriesCache.value[id]) || notFoundCache.value.includes(id);
  const missingLines = lines.value.filter(id => !known(id));
  const newFields = metrics.value.filter(field => !fetchedFields.value.includes(field));
  const cachedLines = lines.value.filter(id => Boolean(seriesCache.value[id]));

  const requests: Promise<void>[] = [];

  // New series arrive with every field fetched so far, not just the selected
  // ones, otherwise a line removed and re-added would be missing the values
  // for a metric that is switched back to later
  if (missingLines.length) {
    const fields = Array.from(new Set(fetchedFields.value.concat(metrics.value)));
    requests.push(
      GetPlotSeries(missingLines, fields).then(response => {
        for (const item of response.series) {
          seriesCache.value[item.id] = item;
        }
        notFoundCache.value = Array.from(
          new Set(notFoundCache.value.concat(response.not_found))
        );
      })
    );
  }

  // Newly selected metrics are backfilled into the series already cached
  if (newFields.length && cachedLines.length) {
    requests.push(
      GetPlotSeries(cachedLines, newFields).then(response => {
        for (const item of response.series) {
          const cached = seriesCache.value[item.id];
          if (!cached) continue;
          const fetched: Record<number, Record<string, any>> = {};
          for (const point of item.points) {
            fetched[point.num] = point.values;
          }
          for (const point of cached.points) {
            point.values = { ...point.values, ...(fetched[point.num] ?? {}) };
          }
        }
      })
    );
  }

  if (!requests.length) {
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(metrics.value)));
    return;
  }

  pending.value += 1;
  loading.value = true;
  try {
    await Promise.all(requests);
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(metrics.value)));
  } finally {
    pending.value -= 1;
    loading.value = pending.value > 0;
  }
}

// Cached series are never re-read, so new models on disk need an explicit reload
async function reload() {
  seriesCache.value = {};
  notFoundCache.value = [];
  fetchedFields.value = [];
  await load();
}

// The URL is the source of truth, every mutation goes through it
async function syncFromQuery() {
  lines.value = parseQuery(route.query.lines);
  metrics.value = parseQuery(route.query.metrics);
  await load();
}

watch(() => route.query, syncFromQuery, { immediate: true });

function onSelect(id: string) {
  if (lines.value.includes(id)) return;
  updateQuery(lines.value.concat([id]), metrics.value);
}

function onRemove(id: string) {
  updateQuery(lines.value.filter(line => line !== id), metrics.value);
}

function removeAllMissing() {
  updateQuery(
    lines.value.filter(line => !notFound.value.includes(line)),
    metrics.value
  );
}

function clearAll() {
  updateQuery([], metrics.value);
}
</script>

<template>
  <NavBar/>
  <div class="content">
    <v-breadcrumbs :items="['Plots']"></v-breadcrumbs>

    <LineSearchBar @select="onSelect"/>

    <v-alert
      v-if="notFound.length"
      type="warning"
      variant="tonal"
      class="mt-4"
    >
      Could not find {{ notFound.length }} of the requested lines in this workspace.
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

    <div v-if="lines.length" class="header-row">
      <span class="text">{{ series.length }} line(s) on the plot</span>
      <v-btn variant="text" size="small" @click="reload">Reload</v-btn>
      <v-btn variant="text" size="small" @click="clearAll">Clear all</v-btn>
    </div>

    <div v-if="series.length" class="line-row">
      <v-chip
        v-for="(item, index) in series"
        :key="item.id"
        :color="seriesColor(index)"
        class="line-chip"
        closable
        variant="flat"
        @click:close="onRemove(item.id)"
      >
        <router-link
          class="line-link"
          :to="{ name: 'model_line', params: { repoName: item.repo, lineName: item.line } }"
        >{{ item.path }}</router-link>
        <span class="line-count">{{ item.points.length }}</span>
      </v-chip>
    </div>

    <v-select
      v-if="plotFields.length"
      v-model="selectedMetric"
      :items="plotFields"
      label="Select metric"
      class="metric-select"
      density="compact"
      variant="outlined"
      :menu-props="{ maxHeight: '300px' }"
      clearable
      hide-details
    />

    <v-progress-linear v-if="loading" indeterminate color="#084C61" class="mt-2"/>

    <MetricChart
      v-if="series.length && selectedMetric"
      :series="series"
      :field="selectedMetric"
    />

    <div v-else-if="!loading" class="empty">
      <template v-if="!lines.length">
        Find lines by their path like <b>repo/line</b> or by its tail like <b>00000</b>.
        Selected lines appear on the plot as separate series.
      </template>
      <template v-else-if="!plotFields.length">
        None of the selected lines have metrics or params to plot.
      </template>
      <template v-else>
        Select a metric to plot it against the model nums of every selected line.
      </template>
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

.line-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.line-chip {
  color: #fff;
}

.line-chip :deep(.v-chip__close) {
  color: #fff;
}

.line-link {
  color: #fff;
  text-decoration: none;
}

.line-count {
  color: #fff;
  opacity: 0.75;
  margin-left: 8px;
}

.metric-select {
  max-width: 300px;
  margin-top: 24px;
}

.empty {
  margin-top: 40px;
  color: #555;
}
</style>
