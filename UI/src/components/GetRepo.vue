<script lang="ts">
import type {Repo} from "@/models/Repo";

export async function Get(repoName: string): Promise<Repo> {
  return fetch('http://localhost:8000/v1/repo', {
    method: "post",
    body: JSON.stringify({"repo": repoName}),
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

</script>
<template>

</template>