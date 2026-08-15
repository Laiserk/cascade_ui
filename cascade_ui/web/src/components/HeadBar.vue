<template>
  <div class="headBar">
    <div class="left-side">
      <router-link to="/">
        <img alt="" class="logo" src="../assets/logo.svg">
      </router-link>
      <router-link class="nav-link" :to="{ name: 'compare' }">
        <v-icon :icon="mdiScaleBalance" size="24"/>
        <span>Compare</span>
        <v-badge
          v-if="store.items.value.length"
          :content="store.items.value.length"
          color="#DB504A"
          text-color="#ffffff"
          inline
        />
      </router-link>
      <router-link class="nav-link" :to="{ name: 'plots' }">
        <v-icon :icon="mdiChartLine" size="24"/>
        <span>Plots</span>
      </router-link>
    </div>
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

.left-side {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #FFFDF5;
  text-decoration: none;
  font-size: 20px;
}

</style>

<script lang="ts" setup>
import IconGitHub from "@/components/icons/IconGithub.vue";
import { useCompareStore } from "@/utils/CompareStore";
import { mdiChartLine, mdiScaleBalance } from "@mdi/js";

const store = useCompareStore();
</script>