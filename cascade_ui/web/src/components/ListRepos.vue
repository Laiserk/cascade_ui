<script setup lang="ts">
import { Workspace } from "@/models/Workspace";
import TagsRow from "@/components/TagsRow.vue";
import { useRouter } from "vue-router";
import {openRepo} from "@/components/Open";

const props = defineProps<{ workspace: Workspace }>();
const router = useRouter();

</script>

<template>
  <div v-for="repo in props.workspace.repos" :key="repo.name">
    <div class="listItem">
      <v-card>
        <v-card-title style="font-family: Roboto,serif; font-size: 20px;">
          {{ repo.name }}
        </v-card-title>
        <v-card-subtitle style="font-family: Roboto,serif; font-size: 14px;">
          {{ repo.len }} lines
        </v-card-subtitle>

        <div class="tags-container">
          <TagsRow v-if="repo.tags" :tags="repo.tags" />
        </div>

        <v-card-actions>
          <v-btn
            style="font-family: Roboto,serif; font-size: 14px; color: #DEB841;"
            text="OPEN"
            @click="openRepo(router, repo.name)"
          >
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<style scoped>
.listItem {
  width: 580px;
  margin-top: 26px;
  box-shadow: 0 4px 4px 0 #00000040;
}
.tags-container {
  width: 100%;
  max-width: 540px;
  margin-left: 15px;
  display: flex;
  flex-wrap: wrap;
}
</style>