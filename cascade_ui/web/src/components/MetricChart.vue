<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import type { PlotSeries } from "@/models/Plots";
import { seriesColor, metricShade } from "@/utils/PlotColors";

const props = defineProps<{ series: PlotSeries[], fields: string[], logScale?: boolean }>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let observer: ResizeObserver | null = null;

function resetZoom() {
  if (!chart) return;
  const models = (chart as any).getModel().queryComponents({ mainType: "dataZoom" });
  const batch = models.map((model: any) => ({ dataZoomId: model.id, start: 0, end: 100 }));
  if (batch.length) chart.dispatchAction({ type: "dataZoom", batch: batch });
}

function numString(num: number) {
  return String(num).padStart(5, "0");
}

const categories = computed(() => {
  const nums = new Set<number>();
  for (const series of props.series) {
    for (const point of series.points) {
      nums.add(point.num);
    }
  }
  return Array.from(nums).sort((a, b) => a - b);
});

const slugs = computed(() => {
  const map: Record<string, Record<number, string | null>> = {};
  for (const series of props.series) {
    map[series.id] = {};
    for (const point of series.points) {
      map[series.id][point.num] = point.slug;
    }
  }
  return map;
});

const chartSeries = computed(() => {
  const curves = [];
  for (const [lineIndex, series] of props.series.entries()) {
    for (const [fieldIndex, field] of props.fields.entries()) {
      const byNum: Record<number, any> = {};
      for (const point of series.points) {
        byNum[point.num] = point.values[field];
      }
      const color = metricShade(
        seriesColor(lineIndex),
        fieldIndex,
        props.fields.length
      );
      curves.push({
        name: props.fields.length > 1 ? `${series.path} · ${field}` : series.path,
        seriesId: series.id,
        field: field,
        type: "line" as const,
        connectNulls: true, // Metrics can be recorded not every step, but we should still connect them
        data: categories.value.map(num => {
          const value = byNum[num];
          if (typeof value !== "number" || isNaN(value)) return null;
          if (props.logScale && value <= 0) return null;
          return value;
        }),
        lineStyle: { color: color },
        itemStyle: { color: color }
      });
    }
  }
  return curves;
});

const droppedPoints = computed(() => {
  if (!props.logScale) return 0;
  let count = 0;
  for (const series of props.series) {
    for (const point of series.points) {
      for (const field of props.fields) {
        const value = point.values[field];
        if (typeof value === "number" && !isNaN(value) && value <= 0) count += 1;
      }
    }
  }
  return count;
});

const curvesByName = computed(() => {
  const map: Record<string, { seriesId: string }> = {};
  for (const curve of chartSeries.value) {
    map[curve.name] = { seriesId: curve.seriesId };
  }
  return map;
});

function render() {
  if (!chart) return;

  chart.setOption({
    legend: {
      type: "scroll",
      bottom: 0,
      data: chartSeries.value.map(series => series.name)
    },
    grid: { bottom: 60 },
    toolbox: {
      iconStyle: { borderColor: "#177E89" },
      emphasis: { iconStyle: { borderColor: "#084C61" } },
      feature: {
        dataZoom: {
          xAxisIndex: 0,
          yAxisIndex: 0,
          title: { zoom: "Box zoom", back: "Undo zoom" }
        },
        // echarts only renders user-defined features whose name starts with "my"
        myResetZoom: {
          show: true,
          title: "Reset zoom",
          // Corner brackets, drawn in the same 0..60 box the built-in icons use
          icon: "M2,20V2H20 M40,2H58V20 M58,40V58H40 M20,58H2V40",
          onclick: resetZoom
        }
      }
    },
    xAxis: {
      type: "category",
      data: categories.value,
      name: "Model Num"
    },
    yAxis: {
      type: props.logScale ? "log" : "value",
      scale: true,
      name: props.fields.length === 1 ? props.fields[0] : ""
    },
    series: chartSeries.value,
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const idx = params[0]?.dataIndex;
        const num = categories.value[idx];
        const rows = params
          .filter((param: any) => param.value !== null && param.value !== undefined)
          .map((param: any) => {
            const curve = curvesByName.value[param.seriesName];
            const slug = curve ? slugs.value[curve.seriesId]?.[num] : null;
            return `${param.marker}${param.seriesName}`
              + `${slug ? ` (${slug})` : ""}: ${param.value}`;
          });
        return `Num: ${numString(num)}<br/>${rows.join("<br/>")}`;
      }
    }
  }, { replaceMerge: ["series"] });
}

onMounted(() => {
  if (!chartRef.value) return;
  chart = echarts.getInstanceByDom(chartRef.value) ?? echarts.init(chartRef.value);
  observer = new ResizeObserver(() => chart?.resize());
  observer.observe(chartRef.value);
  render();
});

onBeforeUnmount(() => {
  observer?.disconnect();
  observer = null;
  chart?.dispose();
  chart = null;
});

watch([chartSeries, () => props.fields, () => props.logScale], render);
</script>

<template>
  <div>
    <div ref="chartRef" class="chart"></div>
    <div v-if="droppedPoints" class="log-note">
      {{ droppedPoints }} value(s) at or below zero are hidden, a log axis cannot place them.
    </div>
  </div>
</template>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
  margin-top: 24px;
}

.log-note {
  color: #555;
  font-size: 13px;
}
</style>
