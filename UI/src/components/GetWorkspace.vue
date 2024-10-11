<script lang="ts" setup>
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

</template>