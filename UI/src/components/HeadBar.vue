<template>
  <div class="headBar">
    <img alt="" class="logo" src="../assets/logo.svg">
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
</style>

<script lang="ts" setup>
import IconGitHub from "@/components/icons/IconGithub.vue";
</script>