<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Box /></el-icon>
      收纳位置
    </div>

    <div v-if="locations.length === 0" class="card">
      <div class="empty-tip">
        <el-icon><Box /></el-icon>
        <p>还没有收纳位置，请在饰品档案中标记收纳位置</p>
      </div>
    </div>

    <div v-else>
      <div class="summary-row">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #c9a96e, #b8956a);">
            <el-icon :size="24" color="#fff"><Box /></el-icon>
          </div>
          <div>
            <div class="stat-num">{{ locations.length }}</div>
            <div class="stat-label">收纳位置</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #9b7ab8, #7a5e94);">
            <el-icon :size="24" color="#fff"><Collection /></el-icon>
          </div>
          <div>
            <div class="stat-num">{{ totalCount }}</div>
            <div class="stat-label">饰品总数</div>
          </div>
        </div>
      </div>

      <div class="loc-grid">
        <div v-for="loc in locations" :key="loc.name" class="loc-card">
          <div class="loc-header">
            <div class="loc-name">
              <el-icon color="#c9a96e"><Location /></el-icon>
              {{ loc.name }}
            </div>
            <el-tag type="warning" effect="light">{{ loc.count }} 件</el-tag>
          </div>
          <div class="loc-items">
            <div v-for="acc in loc.accessories" :key="acc.id" class="mini-item" @click="showDetail(acc)">
              <div class="mini-photo">
                <img v-if="acc.photo" :src="'/uploads/' + acc.photo" />
                <div v-else class="mini-ph-placeholder">
                  <el-icon :size="18"><Picture /></el-icon>
                </div>
              </div>
              <div class="mini-info">
                <div class="mini-name">{{ acc.name }}</div>
                <div class="mini-meta">
                  <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
                  {{ acc.category }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="饰品详情" width="480px">
      <div v-if="currentAcc" class="detail-body">
        <div class="detail-photo">
          <img v-if="currentAcc.photo" :src="'/uploads/' + currentAcc.photo" />
          <div v-else class="detail-ph-empty">
            <el-icon :size="60" color="#ccc"><Picture /></el-icon>
          </div>
        </div>
        <h3 class="detail-name">{{ currentAcc.name }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="品类">{{ currentAcc.category }}</el-descriptions-item>
          <el-descriptions-item label="材质">{{ currentAcc.material }}</el-descriptions-item>
          <el-descriptions-item label="色系">
            <span class="color-dot" :style="{ background: colorMap[currentAcc.color_family] }"></span>
            {{ currentAcc.color_family }}
          </el-descriptions-item>
          <el-descriptions-item label="颜色">{{ currentAcc.color }}</el-descriptions-item>
          <el-descriptions-item label="风格">{{ currentAcc.style }}</el-descriptions-item>
          <el-descriptions-item label="佩戴次数">{{ currentAcc.wear_count }}</el-descriptions-item>
          <el-descriptions-item label="上次佩戴" :span="2">{{ currentAcc.last_worn_date || '未佩戴过' }}</el-descriptions-item>
          <el-descriptions-item label="场合" :span="2">
            <span v-for="o in currentAcc.occasions" :key="o" class="tag-item">{{ o }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStorageLocations } from '@/api'

const locations = ref([])
const detailVisible = ref(false)
const currentAcc = ref(null)

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const totalCount = computed(() => locations.value.reduce((s, l) => s + l.count, 0))

const showDetail = (acc) => {
  currentAcc.value = acc
  detailVisible.value = true
}

const loadData = async () => {
  locations.value = await getStorageLocations()
}

onMounted(loadData)
</script>

<style scoped>
.summary-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: #4a2c2a;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #999;
}

.loc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.loc-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
}

.loc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #f0e8dd;
}

.loc-name {
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
  display: flex;
  align-items: center;
  gap: 6px;
}

.loc-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.mini-item {
  display: flex;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.mini-item:hover {
  background: #faf7f5;
}

.mini-photo {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5efe6;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-ph-placeholder {
  color: #ccc;
}

.mini-info {
  flex: 1;
  min-width: 0;
}

.mini-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.mini-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-body {
  text-align: center;
}

.detail-photo {
  width: 100%;
  height: 220px;
  background: #f5efe6;
  border-radius: 10px;
  margin-bottom: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-ph-empty {
  color: #ccc;
}

.detail-name {
  font-size: 18px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 16px;
}
</style>
