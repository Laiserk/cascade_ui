<script async lang="ts" setup>
import type {Workspace} from "@/models/Workspace";

async function GetWorkspace(): Promise<Workspace> {
  return fetch('http://localhost:8000/v1/workspace', {
    method: "post",
    headers: {
      'Access-Control-Allow-Origin': '*',
      "Content-Type": "application/json"
    }
  })
      .then(res => res.json())
      .catch(function (error) {
        console.log(error);
      });
}

const workspace = await GetWorkspace();

</script>

<template>
  <div v-for="item in workspace.repos">
    <div class="listItem">
      <v-card>
        <v-card-title style="font-family: Roboto,serif; font-size: 20px;">
          {{ item.name }}
        </v-card-title>
        <v-card-subtitle style="font-family: Roboto,serif; font-size: 14px;">
          {{ item.len }} lines
        </v-card-subtitle>
        <v-card-actions>
          <v-btn style="font-family: Roboto,serif; font-size: 14px; color: #1976D2;" text="OPEN">
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
</style>