<template>
  <el-tag :type="map[freq]?.type || 'info'" effect="plain" size="small">
    {{ map[freq]?.label || freq }}
  </el-tag>
</template>

<script setup>
defineProps({
  freq: {
    type: String,
    default: ''
  }
})

const map = {
  '高频': { label: '高频', type: 'success' },
  '中频': { label: '中频', type: 'warning' },
  '低频': { label: '低频', type: 'info' },
  '极少': { label: '极少', type: 'danger' }
}
</script>
