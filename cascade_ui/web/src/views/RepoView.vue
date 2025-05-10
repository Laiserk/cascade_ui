<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import TagsRow from "@/components/TagsRow.vue"
import CommentFeed from "@/components/CommentFeed.vue";
import GetRepo from "@/utils/GetRepo";
import GetWorkspace from "@/utils/GetWorkspace";
import {openLine, openWorkspace} from "@/utils/Open";
import { ref, onMounted, computed } from "vue";
import { Repo as RepoClass } from "@/models/Repo";
import {LinePathSpec} from "@/models/PathSpecs";
import type {Repo} from "@/models/Repo";
import type {Workspace} from "@/models/Workspace";
import { Workspace as WorkspaceClass } from "@/models/Workspace";

import { useRouter, useRoute } from 'vue-router'

const workspace = ref<Workspace | null>(null);

const route = useRoute()
const repoName = computed(() => route.params.repoName as string)

const repo = ref<Repo | null>(null);
const router = useRouter();

const tab = ref(0);

async function loadRepoData() {
  const wsObj = await GetWorkspace();
  workspace.value = wsObj ? new WorkspaceClass(wsObj) : null;
  if (workspace.value && repoName.value) {
    const repoObj = await GetRepo(repoName.value);
    repo.value = new RepoClass(repoObj);
  }
}

onMounted(loadRepoData);

const breadcrumbs = computed(() => {
  if (!workspace.value?.name) return [];
  const wsName = workspace.value.name;
  return [
    {
      title: wsName,
      to: { name: 'main' }
    },
    {
      title: repoName.value,
      disabled: true
    }
  ];
});

const lineHeaders = [
  { title: 'Name', value: 'name' },
  { title: 'Type', value: 'type' },
  { title: 'Len', value: 'len' },
  { title: 'Tags', value: 'tags' },
  { title: 'Created', value: 'created_at' },
  { title: 'Updated', value: 'updated_at' },
];

const processedLines = computed(() => {
  if (!repo.value?.lines) return [];
  return repo.value.lines.map(line => ({
    ...line,
    linePathSpec: new LinePathSpec({
      repo: repoName.value,
      line: line.name,
      lineType: line.type,
    }),
  }));
});

function onBreadcrumbClick(e: any) {
  const item = e?.item;
  if (item?.to && !item.disabled) {
    openWorkspace(router);
  }
}
</script>

<template>
  <div>
    <NavBar/>
    <div class="content">
      <v-breadcrumbs :items="breadcrumbs" @click:item="onBreadcrumbClick"></v-breadcrumbs>
      <v-tabs v-model="tab" class="custom-tabs" grow>
        <v-tab class="custom-tab">General</v-tab>
        <v-tab class="custom-tab">Comments</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <div v-if="tab === 0">
            <div v-if="repo && repo.lines">
              <v-data-table :headers="lineHeaders" :items="processedLines" class="mt-4">
                <template #item.name="{ item }">
                  <v-btn
                    variant="text"
                    style="font-family: Roboto,serif; font-size: 14px; color: #DEB841;"
                    @click="openLine(router, item.linePathSpec)"
                  >
                    {{ item.name }}
                  </v-btn>
                </template>
                <template #item.tags="{ item }">
                  <TagsRow :tags="item.tags" />
                </template>
              </v-data-table>
            </div>
          </div>
        </v-tab-item>
        <v-tab-item>
          <div v-if="tab === 1">
            <CommentFeed
              v-if="repo"
              :comments="repo.comments"
              :pathParts="[repoName]"
              :onCommentSent="loadRepoData"
            />
          </div>
        </v-tab-item>
      </v-tabs-items>
    </div>
  </div>
</template>

<style>
.content {
  margin-left: 60px;
  margin-right: 60px;
}

.custom-tabs {
  background-color: #F5E6B2;
  border-radius: 8px;
}

.custom-tab {
  color: #DEB841 !important;
  background-color: #FFFDF5 !important;
  transition: background 0.2s, color 0.2s;
}

.custom-tab.v-tab--active,
.custom-tab:hover {
  background-color: #E8D496 !important;
  color: #fff !important;
}
</style>