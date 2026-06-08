<template>
  <el-tag :type="statusMap[status]?.type || 'info'" effect="light">
    {{ statusMap[status]?.label || status }}
  </el-tag>
</template>

<script setup>
const props = defineProps({
  status: {
    type: String,
    default: ''
  }
})

const statusMap = {
  in_stock: { label: '在库', type: 'success' },
  lent: { label: '已借出', type: 'primary' },
  overdue: { label: '逾期', type: 'danger' },
  maintenance: { label: '保养中', type: 'warning' },
  repair: { label: '维修中', type: 'warning' },
  lost: { label: '已丢失', type: 'info' },
  inventory_exception: { label: '盘点异常', type: 'danger' }
}
</script>
