<script setup lang="ts">
import { computed, ref, watch } from "vue";
import TagsRow from "./TagsRow.vue";
import type { CompareColumn } from "@/models/Compare";

const props = defineProps<{
  columns: CompareColumn[];
  itemFields: string[];
  selectedFields: string[];
}>();

const emit = defineEmits<{
  (e: "remove", id: string): void;
  (e: "update:selectedFields", fields: string[]): void;
}>();

const baseFields = ["tags", "created_at", "saved_at"];

const hideIdentical = ref(false);
const draftFields = ref<string[]>([...props.selectedFields]);

watch(() => props.selectedFields, fields => {
  draftFields.value = [...fields];
});

function onMenuToggle(open: boolean) {
  if (!open) {
    emit("update:selectedFields", [...draftFields.value]);
  }
}

const fieldsOptions = computed(() => {
  // Fields carried in the URL are kept as options even when no current
  // model has them, otherwise the chips would silently disappear
  return Array.from(new Set(props.itemFields.concat(props.selectedFields))).sort();
});

const allFields = computed(() => {
  const extra = props.selectedFields.filter(field => !baseFields.includes(field));
  return baseFields.concat(extra);
});

function valueOf(column: CompareColumn, field: string) {
  return column.meta ? column.meta[field] : undefined;
}
const canCompare = computed(() => props.columns.length > 1);
const hidingIdentical = computed(() => hideIdentical.value && canCompare.value);

function differs(field: string): boolean {
  if (!canCompare.value) return false;
  const first = JSON.stringify(valueOf(props.columns[0], field) ?? null);
  return props.columns.some(
    column => JSON.stringify(valueOf(column, field) ?? null) !== first
  );
}

const rows = computed(() => {
  return allFields.value
    .map(field => ({ field: field, differs: differs(field) }))
    .filter(row => !hidingIdentical.value || row.differs);
});

function isTags(field: string, value: any): boolean {
  return field === "tags" && Array.isArray(value);
}

function display(value: any): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
</script>

<template>
  <div>
    <div class="controls">
      <v-select
        v-model="draftFields"
        :items="fieldsOptions"
        label="Add meta fields as rows"
        multiple
        chips
        item-title="."
        item-value="."
        :menu-props="{ closeOnContentClick: false }"
        persistent-hint
        hint="Choose which additional rows to display"
        @update:menu="onMenuToggle"
      >
        <template #item="{ props }">
          <v-list-item v-bind="props"></v-list-item>
        </template>
      </v-select>
      <v-switch
        v-model="hideIdentical"
        :disabled="!canCompare"
        :title="canCompare ? '' : 'Add a second model to compare against'"
        label="Hide identical rows"
        color="#084C61"
        hide-details
        style="margin-bottom: 22px; flex: none;"
      />
    </div>

    <div class="table-scroll">
      <v-table class="compare-table" fixed-header>
        <thead>
          <tr>
            <th class="field-column">Field</th>
            <th v-for="column in props.columns" :key="column.id" class="model-column">
              <div class="model-header">
                <router-link
                  class="model-link"
                  :to="{
                    name: 'model',
                    params: {
                      repoName: column.repo,
                      lineName: column.line,
                      modelNumString: column.name
                    }
                  }"
                >
                  {{ column.name }}
                  <v-tooltip activator="parent" location="top">{{ column.path }}</v-tooltip>
                </router-link>
                <v-btn
                  icon="$close"
                  variant="text"
                  size="x-small"
                  :title="`Remove ${column.path} from comparison`"
                  @click="emit('remove', column.id)"
                />
              </div>
            </th>
          </tr>
          <!-- Numbers repeat across lines, the slug sticks together with the header -->
          <tr>
            <th class="field-column">slug</th>
            <th v-for="column in props.columns" :key="column.id" class="slug-cell">
              {{ column.slug }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.field" :class="{ differs: row.differs }">
            <td class="field-column"><b>{{ row.field }}</b></td>
            <td v-for="column in props.columns" :key="column.id">
              <TagsRow
                v-if="isTags(row.field, valueOf(column, row.field))"
                :tags="valueOf(column, row.field)"
              />
              <span v-else>{{ display(valueOf(column, row.field)) }}</span>
            </td>
          </tr>
        </tbody>
      </v-table>
    </div>
  </div>
</template>

<style scoped>
.controls {
  display: flex;
  align-items: flex-end;
  gap: 24px;
}

.table-scroll {
  max-width: 100%;
}

.compare-table {
  min-width: 100%;
}

.compare-table :deep(.v-table__wrapper) {
  max-height: calc(100vh - 340px);
  min-height: 240px;
}

/* Fixed headers are painted with the theme surface colour by default */
.compare-table :deep(thead th) {
  background-color: #FFFDF5 !important;
}

.field-column {
  position: sticky;
  left: 0;
  z-index: 1;
  background-color: #FFFDF5;
  white-space: nowrap;
}

.model-column {
  min-width: 180px;
}

.model-header {
  display: flex;
  align-items: center;
  gap: 4px;
}

.slug-cell {
  font-weight: normal;
  white-space: nowrap;
}

.model-link {
  color: #DEB841;
  font-weight: bold;
  text-decoration: none;
}

.differs {
  background-color: #F5E6B2;
}

.differs .field-column {
  background-color: #F5E6B2;
}
</style>
