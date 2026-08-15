<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import type { PlotSeries } from "@/models/Plots";
import { seriesColor, metricShade } from "@/utils/PlotColors";

const props = defineProps<{ series: PlotSeries[], fields: string[] }>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let observer: ResizeObserver | null = null;

function niceAxisLimits(min: number, max: number) {
  const span = max - min;
  if (span === 0) return [min, max];
  const exponent = Math.floor(Math.log10(span));
  const fraction = span / Math.pow(10, exponent);
  let niceFraction;
  if (fraction <= 1) niceFraction = 1;
  else if (fraction <= 2) niceFraction = 2;
  else if (fraction <= 5) niceFraction = 5;
  else niceFraction = 10;
  const step = niceFraction * Math.pow(10, exponent) / 5;
  const niceMin = Math.floor(min / step) * step;
  const niceMax = Math.ceil(max / step) * step;
  return [niceMin, niceMax];
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
          return typeof value === "number" && !isNaN(value) ? value : null;
        }),
        lineStyle: { color: color },
        itemStyle: { color: color }
      });
    }
  }
  return curves;
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

  const values: number[] = [];
  for (const series of chartSeries.value) {
    for (const value of series.data) {
      if (value !== null) values.push(value);
    }
  }

  let yMin = Math.min(...values);
  let yMax = Math.max(...values);
  if (values.length > 0 && yMin !== yMax) {
    [yMin, yMax] = niceAxisLimits(yMin, yMax);
  } else if (values.length > 0) {
    yMin -= 0.05 * Math.abs(yMin);
    yMax += 0.05 * Math.abs(yMax);
  }

  chart.setOption({
    legend: {
      type: "scroll",
      bottom: 0,
      data: chartSeries.value.map(series => series.name)
    },
    grid: { bottom: 60 },
    xAxis: {
      type: "category",
      data: categories.value,
      name: "Model Num"
    },
    yAxis: {
      type: "value",
      name: props.fields.length === 1 ? props.fields[0] : "",
      min: values.length ? yMin : undefined,
      max: values.length ? yMax : undefined
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

watch([chartSeries, () => props.fields], render);
</script>

<template>
  <div ref="chartRef" class="chart"></div>
</template>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
  margin-top: 24px;
}
</style>
