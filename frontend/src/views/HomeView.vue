<script setup lang="ts">
import PaperList from '@/components/PaperList.vue'
</script>

<template>
  <div class="home">
    <header class="header">
      <h1>Paper Hub</h1>
      <p>科研论文管理与分享平台</p>
    </header>
    
    <PaperList />
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background-color: #007bff;
  color: white;
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 300;
}

.header p {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
}
</style>
