<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavBar from "../components/NavBar.vue";
import LineSearchBar from "@/components/LineSearchBar.vue";
import MetricChart from "@/components/MetricChart.vue";
import GetPlotSeries from "@/utils/GetPlotSeries";
import type { PlotSeries } from "@/models/Plots";
import { seriesColor } from "@/utils/PlotColors";
import { mdiClose, mdiPlus } from "@mdi/js";

const route = useRoute();
const router = useRouter();

const lines = ref<string[]>([]);
const plots = ref<string[][]>([[]]);
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

const allFields = computed(() => Array.from(new Set(plots.value.flat())));

function parseQuery(value: unknown): string[] {
  if (typeof value !== "string" || !value) return [];
  return value.split(",").filter(part => part.length > 0);
}

function parsePlots(value: unknown): string[][] {
  const raw = Array.isArray(value) ? value : [value];
  const parsed = raw
    .filter(part => typeof part === "string")
    .map(part => parseQuery(part));
  // No param at all still means one empty chart with its selector ready
  return parsed.length ? parsed : [[]];
}

function updateQuery(nextLines: string[], nextPlots: string[][]) {
  const query: Record<string, string | string[]> = {};
  if (nextLines.length) query.lines = nextLines.join(",");

  const encoded = nextPlots.map(plot => plot.join(","));
  if (encoded.length > 1 || encoded[0]) {
    query.metrics = encoded;
  }

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
  const newFields = allFields.value.filter(field => !fetchedFields.value.includes(field));
  const cachedLines = lines.value.filter(id => Boolean(seriesCache.value[id]));

  const requests: Promise<void>[] = [];

  if (missingLines.length) {
    const fields = Array.from(new Set(fetchedFields.value.concat(allFields.value)));
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
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(allFields.value)));
    return;
  }

  pending.value += 1;
  loading.value = true;
  try {
    await Promise.all(requests);
    fetchedFields.value = Array.from(new Set(fetchedFields.value.concat(allFields.value)));
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
  plots.value = parsePlots(route.query.metrics);
  await load();
}

watch(() => route.query, syncFromQuery, { immediate: true });

function onSelect(id: string) {
  if (lines.value.includes(id)) return;
  updateQuery(lines.value.concat([id]), plots.value);
}

function onRemove(id: string) {
  updateQuery(lines.value.filter(line => line !== id), plots.value);
}

function removeAllMissing() {
  updateQuery(
    lines.value.filter(line => !notFound.value.includes(line)),
    plots.value
  );
}

function clearAll() {
  updateQuery([], plots.value);
}

function onPlotMetricsUpdate(plotIndex: number, fields: string[]) {
  updateQuery(
    lines.value,
    plots.value.map((plot, index) => (index === plotIndex ? fields : plot))
  );
}

function onAddPlot() {
  const last = plots.value[plots.value.length - 1] ?? [];
  updateQuery(lines.value, plots.value.concat([last.slice()]));
}

function onRemovePlot(plotIndex: number) {
  const kept = plots.value.filter((_, index) => index !== plotIndex);
  updateQuery(lines.value, kept.length ? kept : [[]]);
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

    <v-progress-linear v-if="loading" indeterminate color="#084C61" class="mt-2"/>

    <template v-if="plotFields.length">
    <div
      v-for="(plot, plotIndex) in plots"
      :key="plotIndex"
      class="plot-block"
    >
      <div class="plot-controls">
        <v-select
          :model-value="plot"
          :items="plotFields"
          label="Select metrics"
          class="metric-select"
          density="compact"
          variant="outlined"
          :menu-props="{ maxHeight: '300px', closeOnContentClick: false }"
          multiple
          chips
          closable-chips
          hide-details
          @update:model-value="fields => onPlotMetricsUpdate(plotIndex, fields)"
        />
        <v-btn
          v-if="plots.length > 1"
          icon
          variant="text"
          size="small"
          @click="onRemovePlot(plotIndex)"
        >
          <v-icon :icon="mdiClose"/>
          <v-tooltip activator="parent" location="top">Remove this plot</v-tooltip>
        </v-btn>
      </div>

      <MetricChart
        v-if="series.length && plot.length"
        :series="series"
        :fields="plot"
      />
      <div v-else-if="!loading" class="empty">
        Select a metric to plot it against the model nums of every selected line.
      </div>
    </div>
    </template>

    <div v-if="plotFields.length" class="add-plot-row">
      <v-btn variant="text" size="small" :prepend-icon="mdiPlus" @click="onAddPlot">
        New plot
      </v-btn>
      <span class="add-plot-hint">
        Metrics of different magnitudes are easier to read on separate plots
      </span>
    </div>

    <div v-if="!plotFields.length && !loading" class="empty">
      <template v-if="!lines.length">
        Find lines by their path like <b>repo/line</b> or by its tail like <b>00000</b>.
        Selected lines appear on the plot as separate series.
      </template>
      <template v-else>
        None of the selected lines have metrics or params to plot.
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

.plot-block {
  margin-top: 24px;
  border-top: 1px solid #E0E0E0;
  padding-top: 16px;
}

.plot-block:first-of-type {
  border-top: none;
}

.plot-controls {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.add-plot-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
}

.add-plot-hint {
  color: #555;
  font-size: 13px;
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
