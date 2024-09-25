<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import axios from "axios";


class Repo {
  name: string | null;
  len: number | null;

  constructor(name: string, len: number) {
    this.name = name;
    this.len = len;
  }
}

class Workspace {
  name: string | null;
  len: number | null;
  repos: Repo[] | null

  constructor(name: string, len: number, repos: Repo[]) {
    this.name = name;
    this.len = len;
    this.repos = repos;
  }
}

/*fetch('http://localhost:8000/v1/workspace', {
  method: "post",
  headers: {
    "Content-Type": "application/json"
  }
})
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    })*/
axios.post('http://localhost:8000/v1/workspace',
    {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
    })
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });

/*axios.post('http://localhost:8000/v1/repo',
    {
      repo: 'repo_1'
    })
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });*/

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
      <!--      {{ data }}-->
    </div>
    <!--    <div v-for="item in data">
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
        </div>-->

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