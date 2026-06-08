<template>
  <el-tag :type="map[level]?.type || 'info'" effect="light" size="small">
    <el-icon v-if="showIcon && (level === 'high' || level === 'critical')">
      <WarningFilled />
    </el-icon>
    <el-icon v-else-if="showIcon && level === 'medium'">
      <InfoFilled />
    </el-icon>
    {{ map[level]?.label || level }}
  </el-tag>
</template>

<script setup>
import { WarningFilled, InfoFilled } from '@element-plus/icons-vue'

defineProps({
  level: {
    type: String,
    default: ''
  },
  showIcon: {
    type: Boolean,
    default: true
  }
})

const map = {
  low: { label: '低风险', type: 'success' },
  medium: { label: '中风险', type: 'warning' },
  high: { label: '高风险', type: 'danger' },
  critical: { label: '严重风险', type: 'danger' }
}
</script>
