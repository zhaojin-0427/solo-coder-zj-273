<template>
  <span>{{ formatted }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  date: {
    type: [String, Date],
    default: ''
  },
  format: {
    type: String,
    default: 'YYYY-MM-DD'
  }
})

const pad = (n) => String(n).padStart(2, '0')

const formatted = computed(() => {
  if (!props.date) return '-'
  let d
  if (props.date instanceof Date) {
    d = props.date
  } else {
    d = new Date(props.date)
  }
  if (isNaN(d.getTime())) return '-'
  const year = d.getFullYear()
  const month = pad(d.getMonth() + 1)
  const day = pad(d.getDate())
  const hours = pad(d.getHours())
  const minutes = pad(d.getMinutes())
  const seconds = pad(d.getSeconds())
  return props.format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
})
</script>
