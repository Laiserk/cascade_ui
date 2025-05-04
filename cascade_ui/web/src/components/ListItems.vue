<script setup lang="ts">
import { Line } from "@/models/Line";
import { ref, computed } from "vue";
import { useRouter, useRoute } from 'vue-router'

const props = defineProps<{ line: Line }>();
const selectedFields = ref<string[]>([]);
const requestClicked = ref(false);
const defaultFields = ['name', 'slug', 'tags', 'created_at', 'saved_at'];

const router = useRouter()
const route = useRoute()

const repoName = computed(() => route.params.repoName as string)
const lineName = computed(() => route.params.lineName as string)

const fieldsOptions = computed(() => {
  return props.line?.item_fields.map(field => field.toString()) || [];
});

const dynamicItemHeaders = computed(() => {
  const baseHeaders = [
    { title: 'name', value: 'name' },
    { title: 'slug', value: 'slug' },
    { title: 'tags', value: 'tags' },
    { title: 'created', value: 'created_at' },
    { title: 'saved', value: 'saved_at' },
  ];
  const selected = selectedFields.value
    .filter(f => !baseHeaders.some(h => h.value === f))
    .map(f => ({ title: f, value: f }));
  return baseHeaders.concat(selected);
});

async function fetchLineItems() {
  if (!repoName.value || !lineName.value) return;
  const fields = Array.from(new Set(selectedFields.value));
  const response = await fetch("/v1/line_item_table", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      line_path: { repo: repoName.value, line: lineName.value },
      item_fields: fields,
    }),
  });
  if (response.ok) {
    const items = await response.json();
    if (props.line) {
      const filledItems = items.map((item: Record<string, any>, idx: number) => {
        let existing: Record<string, any> | undefined = undefined;
        if (props.line && Array.isArray(props.line.items)) {
          existing = props.line.items[idx] as Record<string, any>;
        }
        for (const field of defaultFields) {
          if (!(field in item)) {
            if (existing && field in existing) {
              item[field] = existing[field];
            } else {
              item[field] = "";
            }
          }
        }
        return item;
      });
      props.line.items = filledItems;
    }
  }
}

function applyFields() {
  requestClicked.value = true;
  fetchLineItems();
}

function openModel(repoName: string, lineName: string, modelNumString: string) {
  router.push({ name: "model", params: { repoName, lineName, modelNumString } });
}

function openDataset(repoName: string, lineName: string, datasetName: string) {
  router.push({ name: "dataset", params: { repoName, lineName, datasetName } });
}

function unsupportedLineType(type: string) {
  throw new Error(`Unsupported line type: ${type}`);
}

</script>

<template>
    <div v-if="props.line && props.line.items">
        <div class="mb-4" style="display: flex; align-items: flex-end; gap: 8px;">
        <v-select
            v-model="selectedFields"
            :items="fieldsOptions"
            label="Select columns"
            multiple
            chips
            item-title="."
            item-value="."
            :menu-props="{ closeOnContentClick: false }"
            persistent-hint
            hint="Choose which additional columns to display"
        >
            <template #item="{ props }">
            <v-list-item v-bind="props">
            </v-list-item>
            </template>
        </v-select>
        <v-btn
            @click="applyFields"
            color="#D9D7DD"
            style="color: #000; height: 56px; min-width: 64px; margin-bottom: 22px;"
        >Request</v-btn>
        </div>
        <v-data-table :headers="dynamicItemHeaders" :items="line.items" class="mt-4">
        <template #item.name="{ item }">
            <v-btn
                variant="text"
                style="color: #DEB841;"
                @click="props.line.type === 'model_line'
                  ? openModel(repoName, lineName, item.name)
                  : props.line.type === 'data_line'
                    ? openDataset(repoName, lineName, item.name)
                    : unsupportedLineType(props.line.type)"
            >
            {{ item.name }}
            </v-btn>
        </template>
        </v-data-table>
    </div>
</template>
