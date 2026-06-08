<template>
  <el-container style="height: 100%">
    <el-aside width="220px" style="background: linear-gradient(180deg, #4a2c2a 0%, #6b3d3a 100%);">
      <div class="logo">
        <el-icon :size="28" color="#c9a96e"><Cherry /></el-icon>
        <span>饰品管家</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="transparent"
        text-color="#e8dcc8"
        active-text-color="#c9a96e"
        class="side-menu"
      >
        <el-menu-item index="/accessories">
          <el-icon><Collection /></el-icon>
          <span>饰品目录</span>
        </el-menu-item>
        <el-menu-item index="/storage">
          <el-icon><Box /></el-icon>
          <span>收纳位置</span>
        </el-menu-item>
        <el-menu-item index="/recommend">
          <el-icon><MagicStick /></el-icon>
          <span>智能搭配</span>
        </el-menu-item>
        <el-menu-item index="/favorites">
          <el-icon><Star /></el-icon>
          <span>场合收藏</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/trips">
          <el-icon><Suitcase /></el-icon>
          <span>行李规划</span>
        </el-menu-item>
        <el-menu-item index="/tracking">
          <el-icon><Tools /></el-icon>
          <span>借出与保养</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #f0e8dd; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-size: 18px; font-weight: 600; color: #4a2c2a;">
          {{ pageTitle }}
        </div>
        <div style="font-size: 13px; color: #999;">
          <el-icon><Calendar /></el-icon>
          {{ today }}
        </div>
      </el-header>
      <el-main style="background: #faf7f5; padding: 0;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '')

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})
</script>

<style scoped>
.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.side-menu {
  border-right: none;
  padding-top: 10px;
}

.side-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 10px;
  border-radius: 8px;
}

.side-menu .el-menu-item.is-active {
  background: rgba(201, 169, 110, 0.2);
}

.side-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}
</style>
