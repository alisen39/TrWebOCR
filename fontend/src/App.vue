<template>
  <div id="app">
    <a-layout>
      <!-- <a-layout-header>Header</a-layout-header> -->

      <a-layout-content>
        <router-view />
      </a-layout-content>

      <a-layout-footer class="footer" style="background-color:transparent;padding:0.2rem">
        <a href="https://github.com/alisen39/TrWebOCR">TrWebOCR-好用开源的离线OCR（https://github.com/alisen39/TrWebOCR）</a>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<style>
html,
body {
  width: 100%;
  height: 100%;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

}
.footer {
  position: absolute;
  bottom: 0;
  width: 48%;
  text-align: center;
}
.footer a{
  color:#b3b3b3
}
</style>
