<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><MagicStick /></el-icon>
      智能搭配推荐
    </div>

    <div class="card">
      <div class="section-title">选择今日穿搭</div>
      <div class="select-row">
        <div class="select-block">
          <label>主色调</label>
          <div class="color-options">
            <div
              v-for="c in meta.color_families"
              :key="c"
              class="color-option"
              :class="{ active: filters.main_color === c }"
              @click="filters.main_color = filters.main_color === c ? '' : c"
            >
              <span class="swatch" :style="{ background: colorMap[c] }"></span>
              <span>{{ c }}</span>
            </div>
          </div>
        </div>
        <div class="select-block">
          <label>穿搭风格</label>
          <div class="tag-options">
            <el-tag
              v-for="s in meta.styles"
              :key="s"
              :effect="filters.style === s ? 'dark' : 'plain'"
              :type="filters.style === s ? 'warning' : 'info'"
              class="style-tag"
              @click="filters.style = filters.style === s ? '' : s"
            >
              {{ s }}
            </el-tag>
          </div>
        </div>
        <div class="select-block">
          <label>场合</label>
          <div class="tag-options">
            <el-tag
              v-for="o in meta.occasions"
              :key="o"
              :effect="filters.occasion === o ? 'dark' : 'plain'"
              :type="filters.occasion === o ? 'success' : 'info'"
              class="style-tag"
              @click="filters.occasion = filters.occasion === o ? '' : o"
            >
              {{ o }}
            </el-tag>
          </div>
        </div>
      </div>
      <div style="text-align: center; margin-top: 20px;">
        <el-button class="btn-primary" size="large" :icon="MagicStick" @click="doRecommend" :loading="loading">
          生成搭配推荐
        </el-button>
      </div>
    </div>

    <div v-if="results.length > 0">
      <div class="section-title" style="margin-top: 10px;">推荐结果 · 为你找到 {{ results.length }} 套搭配</div>
      <div class="combo-list">
        <div v-for="(r, idx) in results" :key="r.id" class="combo-card">
          <div class="combo-rank">
            <span class="rank-badge" :class="idx < 3 ? 'top' : ''">{{ idx + 1 }}</span>
            <div class="combo-score">
              <el-progress
                type="dashboard"
                :percentage="r.score_percent"
                :width="80"
                color="#c9a96e"
              />
            </div>
          </div>
          <div class="combo-pieces">
            <div class="piece" v-if="r.necklace">
              <div class="piece-photo">
                <img v-if="r.necklace.photo" :src="'/uploads/' + r.necklace.photo" />
                <div v-else class="piece-empty"><el-icon :size="28"><Picture /></el-icon></div>
              </div>
              <div class="piece-label">项链</div>
              <div class="piece-name">{{ r.necklace.name }}</div>
              <div class="piece-tags">
                <span class="color-dot" :style="{ background: colorMap[r.necklace.color_family] }"></span>
                {{ r.necklace.style }}
              </div>
            </div>
            <div class="combo-plus">+</div>
            <div class="piece" v-if="r.earring">
              <div class="piece-photo">
                <img v-if="r.earring.photo" :src="'/uploads/' + r.earring.photo" />
                <div v-else class="piece-empty"><el-icon :size="28"><Picture /></el-icon></div>
              </div>
              <div class="piece-label">耳环</div>
              <div class="piece-name">{{ r.earring.name }}</div>
              <div class="piece-tags">
                <span class="color-dot" :style="{ background: colorMap[r.earring.color_family] }"></span>
                {{ r.earring.style }}
              </div>
            </div>
            <div class="combo-plus">+</div>
            <div class="piece" v-if="r.bracelet">
              <div class="piece-photo">
                <img v-if="r.bracelet.photo" :src="'/uploads/' + r.bracelet.photo" />
                <div v-else class="piece-empty"><el-icon :size="28"><Picture /></el-icon></div>
              </div>
              <div class="piece-label">手链</div>
              <div class="piece-name">{{ r.bracelet.name }}</div>
              <div class="piece-tags">
                <span class="color-dot" :style="{ background: colorMap[r.bracelet.color_family] }"></span>
                {{ r.bracelet.style }}
              </div>
            </div>
          </div>
          <div class="combo-reason">
            <el-icon color="#c9a96e"><ChatDotRound /></el-icon>
            <span>{{ r.reason }}</span>
          </div>
          <div class="combo-actions">
            <el-button size="small" class="btn-primary" @click="saveToFavorites(r)">
              <el-icon><Star /></el-icon>收藏搭配
            </el-button>
            <el-button size="small" type="success" @click="useCombo(r)">
              <el-icon><Check /></el-icon>今日佩戴
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="searched" class="card">
      <div class="empty-tip">
        <el-icon><MagicStick /></el-icon>
        <p>暂无可推荐的搭配组合，请先添加项链、耳环或手链</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { getMeta, getRecommendations, createFavorite, wearAccessory } from '@/api'

const meta = ref({ color_families: [], styles: [], occasions: [] })
const filters = reactive({ main_color: '', style: '', occasion: '' })
const results = ref([])
const loading = ref(false)
const searched = ref(false)

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const loadMeta = async () => {
  meta.value = await getMeta()
}

const doRecommend = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.main_color) params.main_color = filters.main_color
    if (filters.style) params.style = filters.style
    if (filters.occasion) params.occasion = filters.occasion
    results.value = await getRecommendations(params)
    searched.value = true
  } finally {
    loading.value = false
  }
}

const saveToFavorites = async (r) => {
  await createFavorite({
    name: `${filters.main_color || '精选'}搭配`,
    occasion: filters.occasion,
    necklace_id: r.necklace?.id,
    earring_id: r.earring?.id,
    bracelet_id: r.bracelet?.id,
    main_color: filters.main_color,
    style: filters.style,
    notes: r.reason
  })
  ElMessage.success('已收藏到场合收藏')
}

const useCombo = async (r) => {
  const ids = [r.necklace?.id, r.earring?.id, r.bracelet?.id].filter(Boolean)
  for (const id of ids) {
    await wearAccessory(id)
  }
  ElMessage.success('已记录今日佩戴')
}

onMounted(() => {
  loadMeta()
  filters.main_color = '金色'
  filters.style = '优雅'
  doRecommend()
})
</script>

<style scoped>
.select-row {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.select-block label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a2c2a;
  margin-bottom: 10px;
}

.color-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid #e8ddcc;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
  background: #fff;
}

.color-option:hover {
  border-color: #c9a96e;
}

.color-option.active {
  background: #c9a96e;
  color: #fff;
  border-color: #c9a96e;
}

.swatch {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.style-tag {
  cursor: pointer;
  font-size: 13px;
}

.combo-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.combo-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  display: flex;
  align-items: stretch;
  gap: 24px;
}

.combo-rank {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 100px;
  border-right: 1px dashed #f0e8dd;
  padding-right: 20px;
}

.rank-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f5efe6;
  color: #8b6f47;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.rank-badge.top {
  background: linear-gradient(135deg, #c9a96e, #e8c87a);
  color: #fff;
}

.combo-pieces {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.piece {
  flex: 1;
  text-align: center;
}

.piece-photo {
  width: 100%;
  height: 120px;
  background: #f5efe6;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.piece-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.piece-empty {
  color: #ccc;
}

.piece-label {
  font-size: 11px;
  color: #c9a96e;
  font-weight: 600;
  margin-bottom: 4px;
}

.piece-name {
  font-size: 14px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.piece-tags {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.combo-plus {
  font-size: 20px;
  color: #ccc;
  font-weight: 300;
}

.combo-reason {
  flex: 1;
  display: flex;
  gap: 8px;
  padding: 14px;
  background: #faf7f5;
  border-radius: 10px;
  font-size: 13px;
  color: #666;
  line-height: 1.7;
  align-items: flex-start;
}

.combo-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  min-width: 120px;
}

@media (max-width: 900px) {
  .combo-card {
    flex-direction: column;
  }
  .combo-rank {
    flex-direction: row;
    border-right: none;
    border-bottom: 1px dashed #f0e8dd;
    padding-right: 0;
    padding-bottom: 14px;
    min-width: auto;
    justify-content: center;
  }
  .combo-pieces {
    flex-direction: column;
  }
  .combo-plus {
    transform: rotate(90deg);
  }
  .combo-actions {
    flex-direction: row;
  }
}
</style>
