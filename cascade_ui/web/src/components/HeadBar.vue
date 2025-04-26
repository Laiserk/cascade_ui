<template>
  <div class="headBar">
    <router-link to="/">
      <img alt="" class="logo" src="../assets/logo.svg">
    </router-link>
    <a href="https://github.com/Oxid15/cascade">
      <div class="icon" style="margin-right: 10px">
        <IconGitHub/>
      </div>
    </a>
  </div>
</template>

<style scoped>
.headBar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 60px;
  background-color: #084C61;
}

.logo {
  margin-top: 5px;
  width: 60px;
  height: 60px;
}

</style>

<script lang="ts" setup>
import IconGitHub from "@/components/icons/IconGithub.vue";
</script>