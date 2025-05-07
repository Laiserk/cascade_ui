<script setup lang="ts">
import { ref, watchEffect } from 'vue';
import { ModelPathSpec } from '@/models/PathSpecs';
import GetRunConfig from '@/components/GetRunConfig';
import { ConfigResponse } from '@/models/ConfigResponse';

const props = defineProps<{ path: ModelPathSpec }>();
const configData = ref<ConfigResponse | null>(null);
const parsedConfig = ref<{ key: string; value: string; overridden: boolean; oldValue?: string; newValue?: string }[]>([]);

watchEffect(async () => {
  const response = await GetRunConfig(props.path);
  if (response) {
    configData.value = response;
    parseConfig(response);
  }
});

function parseConfig(response: ConfigResponse) {
  const config = (response.config ?? {}) as Record<string, any>;
  const overrides = (response.overrides ?? {}) as Record<string, any>;

  parsedConfig.value = Object.keys(config).map(key => {
    if (key in overrides) {
      return {
        key,
        value: `${config[key]} -> ${overrides[key]}`,
        overridden: true,
        oldValue: config[key],
        newValue: overrides[key]
      };
    } else {
      return {
        key,
        value: config[key],
        overridden: false
      };
    }
  });
}
</script>

<template>
  <div class="config-subheader-container">
    <v-subheader>CONFIG</v-subheader>
  </div>
  <v-data-table
    :items="parsedConfig"
    :headers="[
        { title: 'Key', value: 'key' },
        { title: 'Value', value: 'value' }
    ]"
    item-value="key"
    class="elevation-1"
  >
    <template v-slot:item.value="{ item }">
        <span v-if="item.overridden" class="override-text">{{ item.value }}</span>
        <span v-else>{{ item.value }}</span>
    </template>
  </v-data-table>
</template>

<style scoped>
.config-subheader-container {
  margin-top: 40px;
  margin-bottom: 24px;
}
.override-text {
  color: #db504a;
  font-weight: bold;
}
</style>
