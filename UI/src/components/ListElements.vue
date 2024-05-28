<template>
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