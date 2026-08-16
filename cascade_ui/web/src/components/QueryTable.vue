<script setup lang="ts">
import { useRouter } from "vue-router";
import TagsRow from "./TagsRow.vue";

const props = defineProps<{
  columns: string[];
  rows: Record<string, any>[];
  workspaceRoot: string;
}>();

const router = useRouter();

function display(value: any): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function isTags(column: string, value: any): boolean {
  return column === "tags" && Array.isArray(value);
}

/**
 * Turns an absolute model path into a route to its page.
 *
 * Only model nums are linked: dataset versions live under the same URL
 * pattern and the router resolves that pattern to the model view, so a
 * dataset link would land on the wrong page
 */
function modelRoute(value: any) {
  if (typeof value !== "string" || !props.workspaceRoot) return null;
  if (!value.startsWith(props.workspaceRoot)) return null;

  const parts = value.slice(props.workspaceRoot.length).split("/").filter(Boolean);
  if (parts.length !== 3) return null;

  const [repoName, lineName, num] = parts;
  if (!/^\d+$/.test(num)) return null;

  return router.resolve({
    name: "model",
    params: { repoName: repoName, lineName: lineName, modelNumString: num }
  });
}

function isPath(column: string, value: any): boolean {
  return column === "path" && modelRoute(value) !== null;
}
</script>

<template>
  <div class="table-scroll">
    <v-table class="query-table" fixed-header>
      <thead>
        <tr>
          <th v-for="column in props.columns" :key="column">{{ column }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in props.rows" :key="index">
          <td v-for="column in props.columns" :key="column">
            <TagsRow v-if="isTags(column, row[column])" :tags="row[column]"/>
            <router-link
              v-else-if="isPath(column, row[column])"
              class="model-link"
              :to="modelRoute(row[column])!"
            >{{ row[column] }}</router-link>
            <span v-else>{{ display(row[column]) }}</span>
          </td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<style scoped>
.table-scroll {
  max-width: 100%;
}

.query-table {
  min-width: 100%;
}

.query-table :deep(.v-table__wrapper) {
  max-height: calc(100vh - 420px);
}

.query-table :deep(thead th) {
  background-color: #fff !important;
  white-space: nowrap;
}

.query-table :deep(td) {
  max-width: 480px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-link {
  color: #084C61;
  font-weight: bold;
  text-decoration: none;
}
</style>
