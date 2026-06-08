<template>
  <span
    class="amount-display"
    :style="{
      fontWeight: fontWeight,
      color: color || undefined
    }"
  >{{ prefix }}{{ formatted }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  amount: {
    type: Number,
    default: 0
  },
  prefix: {
    type: String,
    default: '¥'
  },
  precision: {
    type: Number,
    default: 2
  },
  fontWeight: {
    type: [Number, String],
    default: 500
  },
  color: {
    type: String,
    default: ''
  }
})

const formatted = computed(() => {
  const num = Number(props.amount) || 0
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: props.precision,
    maximumFractionDigits: props.precision
  })
})
</script>

<style scoped>
.amount-display {
  font-variant-numeric: tabular-nums;
}
</style>
