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

<style>
.sidebar {
  position: absolute;
  left: 0;
  height: 100%;
  width: 60px;
  background-color: #D9D9D9;
}

.sidebar ul li {
  position: relative;
  list-style-type: none;
  height: 50px;
  width: 70%;
  margin: 1.2rem auto;
}
</style>

<script lang="ts" setup>
import IconInventory from "@/components/icons/IconInventory.vue";
import IconDataBase from "@/components/icons/IconDataBase.vue";
import IconHome from "@/components/icons/IconHome.vue";
</script>