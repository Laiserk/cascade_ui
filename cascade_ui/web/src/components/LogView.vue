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
  <v-card v-if="props.path" style="height: 800px; overflow: auto;">
    <v-divider />
    <v-card-text class="pa-0" style="height: 750px; overflow: auto;">
      <v-progress-linear v-if="loading" indeterminate color="primary" />
      <v-virtual-scroll
        v-else
        :items="logLines"
        height="750"
        item-height="22"
        class="log-scroll"
      >
        <template #default="{ item, index }">
          <div class="d-flex font-mono log-line">
            <span class="log-linenum">{{ index + 1 }}</span>
            <span class="log-content">{{ item }}</span>
          </div>
        </template>
      </v-virtual-scroll>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.log-scroll {
  font-family: 'Fira Mono', 'Consolas', 'Menlo', monospace;
  background: #f3f3f4;
  color: #2f6f8d;
  white-space: pre;
  overflow-x: auto;
  display: flex;
}
.log-line {
  min-height: 22px;
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
.log-content {
  flex: 1;
  white-space: pre;
  overflow-x: auto;
}
</style>