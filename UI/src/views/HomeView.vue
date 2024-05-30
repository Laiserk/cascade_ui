<script setup lang="ts">
import NavBar from "../components/NavBar.vue";
import Content from "../components/Content.vue";
import PageTitle from "@/components/PageTitle.vue";
import ListElements from "@/components/ListElements.vue";
import Label from "@/components/Label.vue";
import SubLabel from "@/components/SubLabel.vue";
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
    <PageTitle>
      Welcome to Cascade!
    </PageTitle>
    <ListElements>
      <ul>
        <li>
          <a>
            <div>
              <Label>
                repo_1
              </Label>
              <SubLabel>
                01-09-2023
              </SubLabel>
            </div>
          </a>
        </li>
        <li>
          <a>
            <div>
              <Label>
                repo_2
              </Label>
              <SubLabel>
                01-09-2023
              </SubLabel>
            </div>
          </a>
        </li>
        <li>
          <a>
            <div>
              <Label>
                repo_3
              </Label>
              <SubLabel>
                01-09-2023
              </SubLabel>
            </div>
          </a>
        </li>
      </ul>
    </ListElements>
  </Content>
  </body>
</template>
<style scoped>

</style>
