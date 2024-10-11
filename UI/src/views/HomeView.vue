<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import ListRepos from "@/components/ListRepos.vue";
</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="stylesheet" href="src/assets/main.css">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap"
          rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap"
        rel="stylesheet">
  </head>
  <body>
  <NavBar/>
  <div class="content">
    <v-breadcrumbs :items="['Workspace', 'Workspace1']"></v-breadcrumbs>
    <div class="welcome">
      Welcome to Cascade!
    </div>
    <Suspense>
      <ListRepos/>
      <template #fallback>
        Loading...
      </template>
    </Suspense>
  </div>
  </body>
</template>


<style>
.content {
  margin-left: 60px;
}

.welcome {
  font-family: 'Montserrat', serif;
  font-style: normal;
  font-weight: 700;
  font-size: 40px;
  line-height: 49px;
  color: #084C61;
}

</style>
