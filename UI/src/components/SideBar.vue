<template>
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
</template>
<script lang="ts" setup>
import IconInventory from "@/components/icons/IconInventory.vue";
import IconDataBase from "@/components/icons/IconDataBase.vue";
import IconHome from "@/components/icons/IconHome.vue";
</script>