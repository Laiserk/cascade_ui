<script setup lang="ts">
import { ref, watch } from 'vue';
import { ModelPathSpec } from '@/models/PathSpecs';
import GetRunLog from '@/utils/GetRunLog';

const props = defineProps<{ path: ModelPathSpec }>();

const logLines = ref<string[]>([]);
const loading = ref(false);

async function fetchLog() {
  if (!props.path) return;
  loading.value = true;
  try {
    const resp = await GetRunLog(props.path);
    logLines.value = (resp?.log_text ?? '').split('\n');
  } finally {
    loading.value = false;
  }
}

watch(() => props.path, fetchLog, { immediate: true });
</script>

<template>
  <v-subheader style="margin-top: 24px; margin-bottom: 24px">LOGS</v-subheader>
  <v-card v-if="props.path" class="log-card">
    <v-divider />
    <v-card-text class="pa-0 log-card-text">
      <v-progress-linear v-if="loading" indeterminate color="primary" />
      <v-virtual-scroll
        v-else
        :items="logLines"
        height="600"
        item-height="22"
        class="log-scroll"
      >
        <template #default="{ item, index }">
          <div class="d-flex font-mono log-line">
            <span class="log-linenum">{{ index + 1 }}</span>
            <span>{{ item }}</span>
          </div>
        </template>
      </v-virtual-scroll>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.log-card {
  display: flex;
  flex-direction: column;
  max-width: 1200px;
}
.log-card-text {
  overflow: auto;
  display: flex;
  flex-direction: column;
}
.log-scroll {
  font-family: 'Fira Mono', 'Consolas', 'Menlo', monospace;
  background: #f3f3f4;
  color: #2f6f8d;
  white-space: pre;
  overflow-x: auto;
  width: 100%;
}
.log-line {
  min-height: 22px;
  display: flex;
  align-items: flex-start;
}
.log-linenum {
  display: inline-block;
  width: 3em;
  color: #888;
  text-align: right;
  margin-right: 1em;
  user-select: none;
  flex-shrink: 0;
}
</style>