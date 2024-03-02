<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import Content from "@/components/Content.vue";
</script>

<template>
  <head>
    <meta charset="utf-8"/>
    <title>List of experiments</title>
    <link rel="stylesheet" href="src/assets/main.css">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap"
          rel="stylesheet">
  </head>
  <body>
  <NavBar/>
  <Content>
    <div class="title">
      <p>Welcome to Cascade!</p>
    </div>
    <div class="listRepos">
      <ul>
        <li>
          <a>
            <div>
              <p class="label">repo_1</p>
              <p class="sub_label">01-09-2023</p>
            </div>
          </a>
        </li>
        <li>
          <a>
            <div>
              <p class="label">repo_2</p>
              <p class="sub_label">01-09-2023</p>
            </div>
          </a>
        </li>
        <li>
          <a>
            <div>
              <p class="label">repo_3</p>
              <p class="sub_label">01-09-2023</p>
            </div>
          </a>
        </li>
      </ul>
    </div>
  </Content>
  </body>
</template>
<style scoped>

.title {
  font-weight: 700;
  font-style: normal;
  font-family: Montserrat, serif;
  font-size: 40px;
  color: #084C61;
  line-height: 49px
}

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


.label {

  font-family: 'Montserrat', serif;
  font-style: normal;
  font-weight: 700;

  font-size: 40px;
  line-height: 48px;

  color: #084C61;
}

.sub_label {

  font-family: 'Montserrat', serif;
  font-style: normal;
  font-weight: 700;
  font-size: 20px;
  line-height: 24px;

  color: #919191;
}


</style>
