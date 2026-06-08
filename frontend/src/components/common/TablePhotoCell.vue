<template>
  <div style="display: flex; align-items: center; gap: 10px;">
    <div
      class="photo-box"
      :style="{ width: size + 'px', height: size + 'px' }"
    >
      <img v-if="photo" :src="'/uploads/' + photo" />
      <el-icon v-else color="#ccc"><Picture /></el-icon>
    </div>
    <div>
      <div style="font-weight: 500;">{{ name }}</div>
      <div style="font-size: 12px; color: #999;">
        {{ category }} · {{ colorFamily }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

defineProps({
  photo: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  category: {
    type: String,
    default: ''
  },
  colorFamily: {
    type: String,
    default: ''
  },
  size: {
    type: Number,
    default: 40
  }
})
</script>

<style scoped>
.photo-box {
  border-radius: 6px;
  background: #f5efe6;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.photo-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
