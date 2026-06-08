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
        <StatCard
          :icon="Box"
          :value="locations.length"
          label="收纳位置"
          icon-color="#c9a96e,#b8956a"
        />
        <StatCard
          :icon="Collection"
          :value="totalCount"
          label="饰品总数"
          icon-color="#9b7ab8,#7a5e94"
        />
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
              <TablePhotoCell
                :photo="acc.photo"
                :name="acc.name"
                :category="acc.category"
                :color-family="acc.color_family"
                :size="44"
              />
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
          <el-descriptions-item label="上次佩戴" :span="2">
            <DateDisplay v-if="currentAcc.last_worn_date" :date="currentAcc.last_worn_date" />
            <span v-else>未佩戴过</span>
          </el-descriptions-item>
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
import { Box, Collection, Location, Picture } from '@element-plus/icons-vue'
import { getStorageLocations } from '@/api'
import StatCard from '@/components/common/StatCard.vue'
import TablePhotoCell from '@/components/common/TablePhotoCell.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'
import { colorMap } from '@/composables/useColorMap'

const locations = ref([])
const detailVisible = ref(false)
const currentAcc = ref(null)

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
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.mini-item:hover {
  background: #faf7f5;
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
