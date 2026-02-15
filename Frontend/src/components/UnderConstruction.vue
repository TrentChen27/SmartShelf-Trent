<template>
  <div class="under-construction">
    <el-icon :size="80" color="#909399"><Tools /></el-icon>
    <h1>{{ title }}</h1>
    <p>This page is under construction and will be available soon.</p>
    <el-button type="primary" @click="$router.back()">Go Back</el-button>
  </div>
</template>

<script setup>
import { Tools } from '@element-plus/icons-vue'

defineProps({
  title: {
    type: String,
    default: 'Under Construction'
  }
})
</script>

<style scoped>
.under-construction {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
}

.under-construction h1 {
  margin: 1rem 0;
  color: #333;
}

.under-construction p {
  color: #666;
  margin-bottom: 2rem;
}
</style>
