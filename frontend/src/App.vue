<script setup lang="ts">
import Layout from './components/Layout.vue'
</script>

<template>
  <Layout />
</template>

<style>
/* 全局样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
  margin: 0 !important;
  padding: 0 !important;
  height: 100%;
  width: 100%;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 强制重置所有可能的容器宽度限制 */
#app,
.app-layout {
  max-width: none !important;
  width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}



/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 深色主题滚动条 */
[data-theme="dark"] ::-webkit-scrollbar-track {
  background: #2c3e50;
}

[data-theme="dark"] ::-webkit-scrollbar-thumb {
  background: #34495e;
}

[data-theme="dark"] ::-webkit-scrollbar-thumb:hover {
  background: #4a5f7a;
}
</style>
