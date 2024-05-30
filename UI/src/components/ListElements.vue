<template>
  <div class="listRepos">
    <slot/>
  </div>
</template>

<style scoped>

.listRepos ul {
  list-style-type: none;
}

.listRepos li {
  float: left;
}

.listRepos li a div p {
}

.listRepos li a div {
  width: 560px;
  height: 248px;
  background: #FFFFFF;
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 27px;
  margin-right: 58px;
}

.listRepos li a:hover {

}

</style>