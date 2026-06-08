<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Star /></el-icon>
      场合收藏
      <el-select v-model="filterOccasion" placeholder="筛选场合" clearable style="margin-left: auto; width: 160px;" @change="loadData">
        <el-option v-for="o in meta.occasions" :key="o" :label="o" :value="o" />
      </el-select>
    </div>

    <div v-if="list.length === 0" class="card">
      <div class="empty-tip">
        <el-icon><Star /></el-icon>
        <p>暂无收藏的搭配，在智能搭配中收藏喜欢的组合吧</p>
      </div>
    </div>

    <div v-else class="fav-grid">
      <div v-for="fav in list" :key="fav.id" class="fav-card">
        <div class="fav-header">
          <div>
            <h4 class="fav-name">{{ fav.name }}</h4>
            <div class="fav-meta">
              <el-tag v-if="fav.occasion" size="small" type="success">{{ fav.occasion }}</el-tag>
              <el-tag v-if="fav.main_color" size="small" type="warning">
                <span class="color-dot" :style="{ background: colorMap[fav.main_color] }"></span>{{ fav.main_color }}
              </el-tag>
              <el-tag v-if="fav.style" size="small">{{ fav.style }}</el-tag>
            </div>
          </div>
          <div class="fav-uses">
            <el-icon color="#c9a96e"><Histogram /></el-icon>
            使用 {{ fav.use_count }} 次
          </div>
        </div>

        <div class="fav-pieces">
          <div class="f-piece" v-if="fav.necklace" :class="{ disabled: fav.necklace.status !== 'in_stock' }">
            <div class="fp-photo">
              <img v-if="fav.necklace.photo" :src="'/uploads/' + fav.necklace.photo" />
              <div v-else class="fp-empty"><el-icon :size="20"><Picture /></el-icon></div>
              <StatusTag
                v-if="fav.necklace.status !== 'in_stock'"
                :status="fav.necklace.status"
                class="fp-status"
              />
            </div>
            <div class="fp-name">{{ fav.necklace.name }}</div>
            <div class="fp-cat">项链</div>
          </div>
          <div class="f-piece" v-if="fav.earring" :class="{ disabled: fav.earring.status !== 'in_stock' }">
            <div class="fp-photo">
              <img v-if="fav.earring.photo" :src="'/uploads/' + fav.earring.photo" />
              <div v-else class="fp-empty"><el-icon :size="20"><Picture /></el-icon></div>
              <StatusTag
                v-if="fav.earring.status !== 'in_stock'"
                :status="fav.earring.status"
                class="fp-status"
              />
            </div>
            <div class="fp-name">{{ fav.earring.name }}</div>
            <div class="fp-cat">耳环</div>
          </div>
          <div class="f-piece" v-if="fav.bracelet" :class="{ disabled: fav.bracelet.status !== 'in_stock' }">
            <div class="fp-photo">
              <img v-if="fav.bracelet.photo" :src="'/uploads/' + fav.bracelet.photo" />
              <div v-else class="fp-empty"><el-icon :size="20"><Picture /></el-icon></div>
              <StatusTag
                v-if="fav.bracelet.status !== 'in_stock'"
                :status="fav.bracelet.status"
                class="fp-status"
              />
            </div>
            <div class="fp-name">{{ fav.bracelet.name }}</div>
            <div class="fp-cat">手链</div>
          </div>
        </div>

        <div v-if="fav.notes" class="fav-notes">
          <el-icon color="#c9a96e" size="14"><ChatDotRound /></el-icon>
          {{ fav.notes }}
        </div>

        <div class="fav-footer">
          <span style="font-size: 12px; color: #999;">创建于 <DateDisplay :date="fav.created_at" /></span>
          <div class="fav-actions">
            <el-button
              size="small"
              type="success"
              :disabled="!isFavAvailable(fav)"
              @click="handleUse(fav)"
            >
              <el-icon><Check /></el-icon>佩戴
            </el-button>
            <el-button size="small" type="danger" text @click="handleDelete(fav)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMeta, getFavorites, useFavorite, deleteFavorite } from '@/api'
import StatusTag from '@/components/common/StatusTag.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'
import { colorMap } from '@/composables/useColorMap'

const meta = ref({ occasions: [] })
const list = ref([])
const filterOccasion = ref('')

const isFavAvailable = (fav) => {
  const items = [fav.necklace, fav.earring, fav.bracelet].filter(Boolean)
  return items.every(a => a.status === 'in_stock')
}

const loadMeta = async () => {
  meta.value = await getMeta()
}

const loadData = async () => {
  const params = filterOccasion.value ? { occasion: filterOccasion.value } : {}
  list.value = await getFavorites(params)
}

const handleUse = async (fav) => {
  await useFavorite(fav.id)
  ElMessage.success(`已记录佩戴「${fav.name}」`)
  loadData()
}

const handleDelete = async (fav) => {
  await ElMessageBox.confirm(`确定删除「${fav.name}」吗？`, '提示', { type: 'warning' })
  await deleteFavorite(fav.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(() => {
  loadMeta()
  loadData()
})
</script>

<style scoped>
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

.fav-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  display: flex;
  flex-direction: column;
}

.fav-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}

.fav-name {
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 8px;
}

.fav-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.fav-uses {
  font-size: 12px;
  color: #8b6f47;
  background: #f5efe6;
  padding: 4px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.fav-pieces {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.fp-photo {
  width: 100%;
  height: 80px;
  background: #f5efe6;
  border-radius: 8px;
  margin-bottom: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.fp-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fp-empty {
  color: #ccc;
}

.fp-status {
  position: absolute;
  top: 4px;
  right: 4px;
}

.f-piece {
  flex: 1;
  text-align: center;
  position: relative;
}

.f-piece.disabled {
  opacity: 0.55;
}

.fp-name {
  font-size: 12px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.fp-cat {
  font-size: 11px;
  color: #c9a96e;
}

.fav-notes {
  font-size: 12px;
  color: #666;
  background: #faf7f5;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 14px;
  line-height: 1.6;
  display: flex;
  gap: 6px;
  align-items: flex-start;
}

.fav-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f0e8dd;
  margin-top: auto;
}

.fav-actions {
  display: flex;
  gap: 6px;
}
</style>
