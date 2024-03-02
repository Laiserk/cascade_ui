<script setup lang="ts">
import IconGitHub from '../components/icons/IconGithub.vue'
import IconHome from "../components/icons/IconHome.vue";
import IconInventory from "../components/icons/IconInventory.vue";
import IconDataBase from "../components/icons/IconDataBase.vue";
</script>

<template>
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
          <a href="/main">
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

<style scoped>
.navbar {
  width: 100%;
  height: 60px;
  background-color: #084C61;
}

.navbar .container {
  height: inherit;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar {
  position: absolute;
  left: 0;
  height: 100%;
  width: 60px;
  background-color: #D9D9D9;
}

.logo {
  width: 60px;
  height: 60px;
}

.icon {
  width: 38px;
  height: 38px;
  fill: #919191;
}

.icon:hover {
  fill: #084C61;
}

.sidebar ul li {
  position: relative;
  list-style-type: none;
  height: 50px;
  width: 70%;
  margin: 1.2rem auto;
}

</style>