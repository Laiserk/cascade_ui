<script setup lang="ts">
import IconGitHub from '../components/icons/IconGithub.vue'
import IconHome from "../components/icons/IconHome.vue";
import IconInventory from "../components/icons/IconInventory.vue";
import IconDataBase from "../components/icons/IconDataBase.vue";
</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="stylesheet" href="src/assets/main.css">
  </head>
  <body>
  <nav class="navbar">
    <div class="container">
      <img class="logo" src="../assets/logo.svg" alt="">
      <a href="https://github.com/Oxid15/cascade">
        <div class="icon" style="margin-right: 10px">
          <IconGitHub/>
        </div>
      </a>
    </div>

    <div class="sidebar">
      <ul>
        <li>
          <a href="/">
            <div class="icon">
              <IconHome/>
            </div>
          </a>
        </li>
        <li>
          <a href="/repos">
            <div class="icon">
              <IconInventory/>
            </div>
          </a>
        </li>
        <li>
          <a href="/data_base">
            <div class="icon">
              <IconDataBase/>
            </div>
          </a>
        </li>
      </ul>
    </div>
  </nav>
  </body>
</template>
