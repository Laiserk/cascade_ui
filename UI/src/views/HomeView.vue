<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="stylesheet" href="src/assets/main.css">
  </head>
  <body>
  <NavBar/>

  <v-breadcrumbs :items="['Workspace']">
    <template v-slot:prepend>
      <v-icon icon="$vuetify" size="small"></v-icon>
    </template>
  </v-breadcrumbs>
  </body>
</template>


<style>

</style>