<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { LinePathSpec } from "@/models/PathSpecs";
import * as echarts from "echarts";
import { fetchLineItems } from "@/components/fetchLineItems";

const props = defineProps<{ line: any, linePath: LinePathSpec }>();

const selectedField = ref<string>("");
const chartData = ref<{ nums: number[], values: number[], slugs: string[] }>({ nums: [], values: [], slugs: [] });
const chartRef = ref<HTMLDivElement | null>(null);

const plotFields = computed(() => props.line?.plot_fields || []);
const defaultFields = computed(() => ["num", "slug", selectedField.value].filter(Boolean));

async function fetchData() {
  if (!selectedField.value || !props.linePath) return;
  if (!fetchLineItems) return;
  await fetchLineItems(
    props.linePath.repo,
    props.linePath.line,
    [selectedField.value, "num", "slug"],
    props.line,
    defaultFields.value
  );
  const items = props.line.items || [];
  chartData.value.nums = items.map((item: any) => item.num);
  chartData.value.values = items.map((item: any) => item[selectedField.value]);
  chartData.value.slugs = items.map((item: any) => item.slug);
}

watch(selectedField, fetchData, { immediate: true });

watch(chartData, () => {
  if (!chartRef.value) return;
  const chart = echarts.init(chartRef.value);

  const values = chartData.value.values.filter(v => typeof v === 'number' && !isNaN(v));
  let yMin = Math.min(...values);
  let yMax = Math.max(...values);
  if (values.length > 0 && yMin !== yMax) {
    const margin = (yMax - yMin) * 0.1;
    yMin -= margin;
    yMax += margin;
  } else if (values.length > 0) {
    yMin -= 0.05 * Math.abs(yMin);
    yMax += 0.05 * Math.abs(yMax);
  }

  chart.setOption({
    xAxis: {
      type: 'category',
      data: chartData.value.nums,
      name: 'Model Num'
    },
    yAxis: {
      type: 'value',
      name: selectedField.value,
      min: values.length ? yMin : undefined,
      max: values.length ? yMax : undefined
    },
    series: [{
      data: chartData.value.values,
      type: 'line',
      smooth: false
    }],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const idx = params[0]?.dataIndex;
        const num = chartData.value.nums[idx];
        const val = chartData.value.values[idx];
        const slug = chartData.value.slugs[idx];
        const numStr = typeof num === "number" ? String(num).padStart(5, "0") : num;
        return `Num: ${numStr}<br/>Slug: ${slug}<br/>${selectedField.value}: ${val}`;
      }
    }
  });
}, { deep: true });

</script>

<template>
  <div v-if="plotFields.length">
    <label for="plot-field-select">Plot field:</label>
    <v-select
      id="plot-field-select"
      v-model="selectedField"
      :items="plotFields"
      label="Select field"
      dense
      outlined
      style="max-width: 300px"
      :menu-props="{ maxHeight: '300px' }"
      hide-details
    />
    <div v-show="selectedField" ref="chartRef" style="width: 100%; height: 400px; margin-top: 24px;"></div>
  </div>
  <div v-else>
    No plot fields available.
  </div>
</template>
