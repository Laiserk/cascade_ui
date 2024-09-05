<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import {useFetch} from "@vueuse/core"

class Repo {
  name: string | null;
  type: string | null
  len: number | null

  constructor(name: string, type: string, len: number) {
    this.name = name;
    this.type = type;
    this.len = len;
  }
}

/*const useMyFetch = createFetch({
  baseUrl: 'http://localhost:8000',
  fetchOptions: {
    method: "post",
    mode: 'no-cors'
  }
});*/

/*let data : Repo[] | null
({ data } = useMyFetch('/v1/repos'));*/

let data: Repo[]
({data} = useFetch('http://localhost:8000/v1/repos', {mode: "no-cors"}).post());

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
      {{ data }}
    </div>
    <div v-for="item in data">
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

  </div>
  </body>
</template>


<style>
.content {
  margin-left: 60px;
}

.listItem {
  width: 580px;
  margin-top: 26px;
  box-shadow: 0 4px 4px 0 #00000040;
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