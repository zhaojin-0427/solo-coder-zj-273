<template>
  <div
    class="stat-card"
    :class="{ clickable: clickable }"
    @click="handleClick"
  >
    <div
      class="stat-ic"
      :style="{ background: `linear-gradient(135deg, ${iconColor})` }"
    >
      <component :is="icon" :size="22" color="#fff" />
    </div>
    <div>
      <div class="stat-v">{{ value }}</div>
      <div class="stat-l">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  icon: {
    type: [Object, Function],
    required: true
  },
  value: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  iconColor: {
    type: String,
    default: '#c9a96e,#e8c87a'
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  transition: all 0.2s;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(74, 44, 42, 0.1);
}

.stat-ic {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-v {
  font-size: 24px;
  font-weight: 700;
  color: #4a2c2a;
  line-height: 1.2;
}

.stat-l {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
</style>
