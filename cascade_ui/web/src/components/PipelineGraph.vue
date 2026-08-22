<script setup lang="ts">
import {ref, shallowRef, watch, onMounted, computed} from "vue";
import {VueFlow, Handle, Position, type NodeMouseEvent} from "@vue-flow/core";
import type {Edge, Node} from "@vue-flow/core";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import GetPipeline from "@/utils/GetPipeline";
import LayoutPipeline from "@/utils/LayoutPipeline";
import type {PipelineNode} from "@/models/Pipeline";

const props = defineProps<{
  repo: string;
  line: string;
  ver: string;
}>();

const nodes = shallowRef<Node[]>([]);
const edges = shallowRef<Edge[]>([]);
const loading = ref(false);
const selected = ref<PipelineNode | null>(null);

async function loadPipeline() {
  loading.value = true;
  selected.value = null;
  try {
    const pipeline = await GetPipeline(props.repo, props.line, props.ver);
    if (!pipeline || !pipeline.nodes) {
      nodes.value = [];
      edges.value = [];
      return;
    }
    const laid = LayoutPipeline(pipeline);
    nodes.value = laid.nodes;
    edges.value = laid.edges;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPipeline);

watch(
  () => [props.repo, props.line, props.ver],
  () => {
    loadPipeline();
  }
);

function onNodeClick(event: NodeMouseEvent) {
  selected.value = event.node.data as PipelineNode;
}

const HIDDEN_FIELDS = ["name"];

const selectedFields = computed(() => {
  const meta = selected.value?.meta;
  if (!meta) return [];
  return Object.entries(meta)
    .filter(([key, value]) => {
      if (HIDDEN_FIELDS.includes(key)) return false;
      if (value === null || value === undefined) return false;
      if (Array.isArray(value) && value.length === 0) return false;
      return true;
    })
    .map(([key, value]) => ({
      key: key,
      value: typeof value === "object" ? JSON.stringify(value, null, 2) : String(value)
    }));
});
</script>

<template>
  <div class="pipeline-tab">
    <div class="pipeline-canvas">
      <div v-if="loading" class="pipeline-placeholder">Loading pipeline...</div>
      <div v-else-if="!nodes.length" class="pipeline-placeholder">
        No pipeline steps found in the meta of this dataset
      </div>
      <VueFlow
        v-else
        :nodes="nodes"
        :edges="edges"
        :fit-view-on-init="true"
        :min-zoom="0.2"
        :max-zoom="2"
        :nodes-draggable="false"
        :nodes-connectable="false"
        :elements-selectable="true"
        @node-click="onNodeClick"
      >
        <template #node-step="stepProps">
          <div class="step-node" :class="{ active: selected?.id === stepProps.data.id }">
            <Handle type="target" :position="Position.Top" :connectable="false"/>
            <div class="step-label">{{ stepProps.data.label }}</div>
            <div class="step-name">{{ stepProps.data.name }}</div>
            <Handle type="source" :position="Position.Bottom" :connectable="false"/>
          </div>
        </template>
      </VueFlow>
    </div>

    <div v-if="selected" class="step-panel">
      <div class="step-panel-header">
        <p class="step-panel-title">{{ selected.label }}</p>
        <button class="step-panel-close" @click="selected = null">×</button>
      </div>
      <p class="step-panel-path">{{ selected.name }}</p>
      <v-table v-if="selectedFields.length" density="compact">
        <tbody>
          <tr v-for="field in selectedFields" :key="field.key">
            <td class="step-panel-key">{{ field.key }}</td>
            <td class="step-panel-value">
              <pre>{{ field.value }}</pre>
            </td>
          </tr>
        </tbody>
      </v-table>
      <p v-else class="step-panel-path">This step has no meta besides its name</p>
    </div>
  </div>
</template>

<style scoped>
.pipeline-tab {
  position: relative;
  margin-top: 20px;
  width: 100%;
}
.pipeline-canvas {
  height: 640px;
  border: 1px solid #E5E4E7;
  border-radius: 8px;
  background: #FBFBFB;
}
.pipeline-placeholder {
  font-family: Roboto;
  font-size: 18px;
  color: #898989;
  padding: 20px;
}
.step-node {
  width: 220px;
  height: 64px;
  box-sizing: border-box;
  padding: 8px 12px;
  border: 1px solid #D9D7DD;
  border-radius: 8px;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.step-node:hover {
  border-color: #DB504A;
}
.step-node.active {
  border-color: #DB504A;
  box-shadow: 0 0 0 2px rgba(219, 80, 74, 0.2);
}
.step-label {
  font-family: Roboto;
  font-weight: bold;
  font-size: 16px;
  color: #DB504A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.step-name {
  font-family: Roboto;
  font-size: 11px;
  color: #898989;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.step-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 340px;
  height: 640px;
  box-sizing: border-box;
  overflow-y: auto;
  background: #FFFFFF;
  border: 1px solid #E5E4E7;
  border-radius: 8px;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.06);
  padding: 16px;
  z-index: 5;
}
.step-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.step-panel-title {
  font-family: Roboto;
  font-weight: bold;
  font-size: 20px;
  color: #DB504A;
  margin: 0;
}
.step-panel-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
  color: #898989;
}
.step-panel-path {
  font-family: Roboto;
  font-size: 13px;
  color: #898989;
  word-break: break-all;
  margin-bottom: 12px;
}
.step-panel-key {
  font-family: Roboto;
  font-size: 14px;
  color: #555;
  vertical-align: top;
  white-space: nowrap;
}
.step-panel-value {
  font-family: Roboto;
  font-size: 14px;
  color: #898989;
}
.step-panel-value pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Roboto;
}
</style>
