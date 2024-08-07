<template>
  <div class="container">
    <img alt="" class="logo" src="../assets/logo.svg">
    <a href="https://github.com/Oxid15/cascade">
      <div class="icon" style="margin-right: 10px">
        <IconGitHub/>
      </div>
    </a>
  </div>
</template>
<script>
import IconGithub from "@/components/icons/IconGithub.vue";

export default {
  name: 'HeadBar',
  components: {IconGithub}
}
</script>