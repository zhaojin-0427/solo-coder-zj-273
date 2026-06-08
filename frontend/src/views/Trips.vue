<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Suitcase /></el-icon>
      旅行/活动搭配行李规划
      <el-button class="btn-primary" style="margin-left: auto;" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新建行程
      </el-button>
    </div>

    <div v-if="!currentTrip">
      <div v-if="trips.length === 0" class="card">
        <div class="empty-tip">
          <el-icon><Suitcase /></el-icon>
          <p>还没有行程计划，点击右上角创建新的旅行或活动搭配清单</p>
        </div>
      </div>

      <div v-else class="trip-list">
        <div v-for="trip in trips" :key="trip.id" class="trip-card" @click="viewTrip(trip.id)">
          <div class="trip-header">
            <h4 class="trip-name">{{ trip.name }}</h4>
            <el-tag :type="trip.status === 'completed' ? 'success' : trip.status === 'packing' ? 'warning' : 'info'" size="small">
              {{ statusMap[trip.status] || '规划中' }}
            </el-tag>
          </div>
          <div class="trip-meta">
            <div class="meta-item">
              <el-icon><Location /></el-icon>
              {{ trip.destination || '未指定目的地' }}
            </div>
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ trip.start_date }} ~ {{ trip.end_date }}
            </div>
            <div class="meta-item">
              <el-icon><Sunny /></el-icon>
              {{ trip.temp_min }}°C ~ {{ trip.temp_max }}°C
            </div>
          </div>
          <div class="trip-tags">
            <el-tag v-if="trip.main_color" size="small" type="warning">
              <span class="color-dot" :style="{ background: colorMap[trip.main_color] }"></span>{{ trip.main_color }}
            </el-tag>
            <el-tag v-if="trip.style" size="small">{{ trip.style }}</el-tag>
            <el-tag v-if="trip.main_occasion" size="small" type="success">{{ trip.main_occasion }}</el-tag>
          </div>
          <div class="trip-footer">
            <span style="font-size: 12px; color: #999;">共 {{ trip.days?.length || 0 }} 天</span>
            <el-button size="small" type="primary" text @click.stop="viewTrip(trip.id)">
              查看详情 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-else>
      <div class="back-bar">
        <el-button text @click="currentTrip = null; loadTrips()">
          <el-icon><ArrowLeft /></el-icon> 返回行程列表
        </el-button>
      </div>

      <div class="card trip-overview">
        <div class="ov-header">
          <div>
            <h2 class="ov-title">{{ currentTrip.name }}</h2>
            <div class="ov-meta">
              <el-icon><Location /></el-icon> {{ currentTrip.destination || '未指定' }}
              <span class="sep">·</span>
              <el-icon><Calendar /></el-icon> {{ currentTrip.start_date }} ~ {{ currentTrip.end_date }}
              <span class="sep">·</span>
              <el-icon><Sunny /></el-icon> {{ currentTrip.temp_min }}°C ~ {{ currentTrip.temp_max }}°C
            </div>
          </div>
          <div class="ov-actions">
            <el-button size="small" @click="openEditDialog">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button size="small" @click="handleRegenerate">
              <el-icon><Refresh /></el-icon> 重新生成
            </el-button>
            <el-button size="small" class="btn-primary" @click="handleExport">
              <el-icon><Download /></el-icon> 导出清单
            </el-button>
            <el-button size="small" type="danger" text @click="handleDelete">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="stat-cards-mini">
          <div class="stat-card-mini">
            <div class="scm-icon" style="background: linear-gradient(135deg, #c9a96e, #e8c87a);">
              <el-icon :size="18" color="#fff"><Box /></el-icon>
            </div>
            <div>
              <div class="scm-value">{{ currentTrip.packed_count }}/{{ currentTrip.total_item_count }}</div>
              <div class="scm-label">打包进度</div>
            </div>
            <el-progress type="dashboard" :percentage="currentTrip.packing_rate" :width="60" color="#c9a96e" />
          </div>
          <div class="stat-card-mini">
            <div class="scm-icon" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
              <el-icon :size="18" color="#fff"><Collection /></el-icon>
            </div>
            <div>
              <div class="scm-value">{{ currentTrip.unique_accessory_count }} 件</div>
              <div class="scm-label">携带饰品数</div>
            </div>
          </div>
          <div class="stat-card-mini">
            <div class="scm-icon" style="background: linear-gradient(135deg, #6ba878, #8ac492);">
              <el-icon :size="18" color="#fff"><RefreshRight /></el-icon>
            </div>
            <div>
              <div class="scm-value">{{ currentTrip.reuse_rate }}%</div>
              <div class="scm-label">饰品复用率</div>
            </div>
          </div>
          <div class="stat-card-mini">
            <div class="scm-icon" style="background: linear-gradient(135deg, #e8b4a0, #f0c8b8);">
              <el-icon :size="18" color="#fff"><Calendar /></el-icon>
            </div>
            <div>
              <div class="scm-value">{{ currentTrip.days?.length || 0 }} 天</div>
              <div class="scm-label">行程天数</div>
            </div>
          </div>
        </div>

        <div class="ov-actions-row">
          <el-button size="small" type="success" @click="handlePackAll">
            <el-icon><Select /></el-icon> 一键全部标记已打包
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="trip-tabs">
        <el-tab-pane label="每日推荐组合" name="days">
          <div v-for="day in currentTrip.days" :key="day.id" class="day-card card">
            <div class="day-header">
              <div class="day-title">
                <span class="day-badge">D{{ day.day_index + 1 }}</span>
                <span class="day-date">{{ day.date }}</span>
                <el-tag v-if="day.occasion" size="small" type="success" style="margin-left: 10px;">
                  {{ day.occasion }}
                </el-tag>
                <el-tag v-if="day.weather" size="small" type="info">
                  <el-icon><PartlyCloudy /></el-icon> {{ day.weather }}
                </el-tag>
              </div>
              <div class="day-actions">
                <el-button size="small" type="primary" text @click="handleSaveDayFavorite(day)">
                  <el-icon><Star /></el-icon> 收藏此搭配
                </el-button>
              </div>
            </div>

            <div class="section-subtitle">
              <el-icon color="#c9a96e"><MagicStick /></el-icon> 精选推荐
            </div>
            <div class="pieces-row">
              <div v-for="item in day.items.filter(i => !i.is_spare)" :key="item.id" class="piece-card" :class="{ packed: item.packed }">
                <div class="pc-checkbox" @click.stop="handleTogglePack(item)">
                  <el-checkbox :model-value="item.packed" />
                </div>
                <div class="pc-photo">
                  <img v-if="item.accessory.photo" :src="'/uploads/' + item.accessory.photo" />
                  <div v-else class="pc-empty"><el-icon :size="24"><Picture /></el-icon></div>
                </div>
                <div class="pc-info">
                  <div class="pc-cat">{{ item.accessory.category }}</div>
                  <div class="pc-name">{{ item.accessory.name }}</div>
                  <div class="pc-tags">
                    <span class="color-dot" :style="{ background: colorMap[item.accessory.color_family] }"></span>
                    {{ item.accessory.color_family }} · {{ item.accessory.style }}
                  </div>
                </div>
                <div v-if="item.reuse_count > 1" class="pc-reuse">
                  <el-icon><RefreshRight /></el-icon> x{{ item.reuse_count }}
                </div>
              </div>
            </div>

            <div v-if="day.items.filter(i => i.is_spare).length > 0">
              <div class="section-subtitle">
                <el-icon color="#e8a45b"><Present /></el-icon> 备用单品
              </div>
              <div class="pieces-row">
                <div v-for="item in day.items.filter(i => i.is_spare)" :key="item.id" class="piece-card spare" :class="{ packed: item.packed }">
                  <div class="pc-checkbox" @click.stop="handleTogglePack(item)">
                    <el-checkbox :model-value="item.packed" />
                  </div>
                  <div class="pc-photo">
                    <img v-if="item.accessory.photo" :src="'/uploads/' + item.accessory.photo" />
                    <div v-else class="pc-empty"><el-icon :size="24"><Picture /></el-icon></div>
                  </div>
                  <div class="pc-info">
                    <div class="pc-cat">{{ item.accessory.category }}</div>
                    <div class="pc-name">{{ item.accessory.name }}</div>
                    <div class="pc-tags">
                      <span class="color-dot" :style="{ background: colorMap[item.accessory.color_family] }"></span>
                      {{ item.accessory.color_family }} · {{ item.accessory.style }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="reason-box">
              <el-icon color="#c9a96e"><ChatDotRound /></el-icon>
              <div class="reason-list">
                <div v-for="(item, idx) in day.items.filter(i => !i.is_spare)" :key="idx" class="reason-item">
                  <strong>{{ item.accessory.category }}:</strong> {{ item.reason }}
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="收纳取件位置" name="storage">
          <div class="card">
            <div class="section-title">收纳取件指引</div>
            <div v-if="!currentTrip.storage_locations?.length" class="empty-tip" style="padding: 30px;">
              <el-icon><Box /></el-icon>
              <p>暂无收纳位置信息</p>
            </div>
            <div v-else class="storage-list">
              <div v-for="loc in currentTrip.storage_locations" :key="loc.location" class="storage-card">
                <div class="storage-header">
                  <el-icon color="#c9a96e"><Location /></el-icon>
                  <span class="storage-name">{{ loc.location }}</span>
                  <el-tag size="small" type="warning">{{ loc.count }} 件</el-tag>
                </div>
                <div class="storage-items">
                  <div v-for="acc in loc.accessories" :key="acc.id" class="storage-item">
                    <div class="si-photo">
                      <img v-if="acc.photo" :src="'/uploads/' + acc.photo" />
                      <el-icon v-else color="#ccc"><Picture /></el-icon>
                    </div>
                    <div class="si-info">
                      <div class="si-name">{{ acc.name }}</div>
                      <div class="si-meta">
                        <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
                        {{ acc.category }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="重复利用率" name="reuse">
          <div class="card">
            <div class="section-title">饰品重复利用统计</div>
            <div v-if="reuseList.length === 0" class="empty-tip" style="padding: 30px;">
              <el-icon><RefreshRight /></el-icon>
              <p>暂无复用数据</p>
            </div>
            <div v-else>
              <el-table :data="reuseList" stripe>
                <el-table-column label="饰品" min-width="200">
                  <template #default="{ row }">
                    <div style="display: flex; align-items: center; gap: 10px;">
                      <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                        <img v-if="row.accessory.photo" :src="'/uploads/' + row.accessory.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                        <el-icon v-else color="#ccc"><Picture /></el-icon>
                      </div>
                      <div>
                        <div style="font-weight: 500;">{{ row.accessory.name }}</div>
                        <div style="font-size: 12px; color: #999;">{{ row.accessory.category }} · {{ row.accessory.material }}</div>
                      </div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="色系" width="100">
                  <template #default="{ row }">
                    <span class="color-dot" :style="{ background: colorMap[row.accessory.color_family] }"></span>
                    {{ row.accessory.color_family }}
                  </template>
                </el-table-column>
                <el-table-column label="使用天数" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag type="warning" effect="light">{{ row.count }} 天</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="复用率" width="140">
                  <template #default="{ row }">
                    <el-progress :percentage="row.percentage" :color="'#c9a96e'" :stroke-width="8" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="缺失风险" name="risk">
          <div class="card">
            <div class="section-title">
              缺失风险提醒
              <el-tag type="info" effect="light" style="margin-left: 10px;">高频使用单品建议携带备用</el-tag>
            </div>
            <div v-if="!currentTrip.missing_risks?.length" class="empty-tip" style="padding: 30px;">
              <el-icon><SuccessFilled /></el-icon>
              <p>所有饰品使用率分布均衡，暂无明显缺失风险</p>
            </div>
            <div v-else class="risk-list">
              <div v-for="risk in currentTrip.missing_risks" :key="risk.accessory.id" class="risk-card" :class="'risk-' + risk.risk_level">
                <div class="risk-badge" :class="'badge-' + risk.risk_level">{{ risk.risk_level }}风险</div>
                <div class="risk-info">
                  <div class="ri-name">
                    {{ risk.accessory.name }}
                    <span style="color: #999; font-weight: normal; font-size: 13px; margin-left: 8px;">
                      {{ risk.accessory.category }}
                    </span>
                  </div>
                  <div class="ri-meta">
                    <span class="color-dot" :style="{ background: colorMap[risk.accessory.color_family] }"></span>
                    {{ risk.accessory.color_family }} · {{ risk.accessory.style }}
                    <span class="sep">·</span>
                    预计使用 {{ risk.usage_days }}/{{ risk.total_days }} 天 ({{ risk.usage_ratio }}%)
                  </div>
                  <div class="ri-suggestion">
                    <el-icon color="#e8a45b"><Warning /></el-icon>
                    {{ risk.suggestion }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑行程' : '新建行程'" width="640px">
      <el-form :model="form" ref="formRef" :rules="rules" label-width="100px">
        <el-form-item label="行程名称" prop="name">
          <el-input v-model="form.name" placeholder="如：三亚度假、年会活动" />
        </el-form-item>
        <el-form-item label="目的地">
          <el-input v-model="form.destination" placeholder="如：海南三亚" />
        </el-form-item>
        <el-form-item label="日期范围" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低温度">
              <el-input-number v-model="form.temp_min" :min="-20" :max="50" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高温度">
              <el-input-number v-model="form.temp_max" :min="-20" :max="50" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="活动场合">
          <el-select v-model="form.main_occasion" placeholder="选择主要场合" clearable style="width: 100%;">
            <el-option v-for="o in meta.occasions" :key="o" :label="o" :value="o" />
          </el-select>
        </el-form-item>
        <el-form-item label="穿搭主色调">
          <div class="color-options">
            <div
              v-for="c in meta.color_families"
              :key="c"
              class="color-option"
              :class="{ active: form.main_color === c }"
              @click="form.main_color = form.main_color === c ? '' : c"
            >
              <span class="swatch" :style="{ background: colorMap[c] }"></span>
              <span>{{ c }}</span>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="风格偏好">
          <div class="tag-options">
            <el-tag
              v-for="s in meta.styles"
              :key="s"
              :effect="form.style === s ? 'dark' : 'plain'"
              :type="form.style === s ? 'warning' : 'info'"
              class="style-tag"
              @click="form.style = form.style === s ? '' : s"
            >
              {{ s }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%;">
            <el-option label="规划中" value="planning" />
            <el-option label="打包中" value="packing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="行程备注..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmit">
          {{ editing ? '保存' : '创建并生成搭配' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exportVisible" title="导出打包清单" width="600px">
      <div class="export-content">
        <pre>{{ exportContent }}</pre>
      </div>
      <template #footer>
        <el-button @click="copyExport">
          <el-icon><DocumentCopy /></el-icon> 复制到剪贴板
        </el-button>
        <el-button class="btn-primary" @click="downloadExport">
          <el-icon><Download /></el-icon> 下载为TXT
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Suitcase, Plus, Location, Calendar, Sunny, ArrowRight, ArrowLeft, Edit, Refresh, Download, Delete, Box, Collection, RefreshRight, MagicStick, PartlyCloudy, Present, Star, Select, Picture, Warning, SuccessFilled, DocumentCopy, Check } from '@element-plus/icons-vue'
import {
  getMeta, getTrips, getTrip, createTrip, updateTrip, deleteTrip,
  regenerateTrip, togglePackItem, packAllItems, saveTripFavorite, exportTrip
} from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const meta = ref({ color_families: [], styles: [], occasions: [] })
const trips = ref([])
const currentTrip = ref(null)
const activeTab = ref('days')
const dialogVisible = ref(false)
const editing = ref(false)
const formRef = ref(null)
const exportVisible = ref(false)
const exportContent = ref('')

const statusMap = {
  planning: '规划中',
  packing: '打包中',
  completed: '已完成'
}

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const defaultForm = () => ({
  id: null,
  name: '',
  destination: '',
  dateRange: [],
  temp_min: 20,
  temp_max: 28,
  main_occasion: '',
  main_color: '',
  style: '',
  status: 'planning',
  notes: ''
})
const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入行程名称', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择日期范围', trigger: 'change' }]
}

const reuseList = computed(() => {
  if (!currentTrip.value?.days) return []
  const map = {}
  const totalDays = currentTrip.value.days.length
  currentTrip.value.days.forEach(day => {
    day.items.forEach(item => {
      const accId = item.accessory_id
      if (!map[accId]) {
        map[accId] = { accessory: item.accessory, count: 0 }
      }
      map[accId].count += 1
    })
  })
  return Object.values(map)
    .filter(x => x.count > 1)
    .map(x => ({
      ...x,
      percentage: Math.round(x.count / totalDays * 100)
    }))
    .sort((a, b) => b.count - a.count)
})

const loadMeta = async () => {
  meta.value = await getMeta()
}

const loadTrips = async () => {
  trips.value = await getTrips()
}

const viewTrip = async (id) => {
  currentTrip.value = await getTrip(id)
}

const openCreateDialog = () => {
  editing.value = false
  Object.assign(form, defaultForm())
  dialogVisible.value = true
}

const openEditDialog = () => {
  if (!currentTrip.value) return
  editing.value = true
  Object.assign(form, {
    id: currentTrip.value.id,
    name: currentTrip.value.name,
    destination: currentTrip.value.destination,
    dateRange: currentTrip.value.start_date && currentTrip.value.end_date
      ? [currentTrip.value.start_date, currentTrip.value.end_date]
      : [],
    temp_min: currentTrip.value.temp_min,
    temp_max: currentTrip.value.temp_max,
    main_occasion: currentTrip.value.main_occasion,
    main_color: currentTrip.value.main_color,
    style: currentTrip.value.style,
    status: currentTrip.value.status,
    notes: currentTrip.value.notes
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const data = {
    name: form.name,
    destination: form.destination,
    start_date: form.dateRange?.[0] || '',
    end_date: form.dateRange?.[1] || '',
    temp_min: form.temp_min,
    temp_max: form.temp_max,
    main_occasion: form.main_occasion,
    main_color: form.main_color,
    style: form.style,
    status: form.status,
    notes: form.notes
  }
  if (editing.value) {
    await updateTrip(form.id, data)
    ElMessage.success('已更新')
    viewTrip(form.id)
  } else {
    const newTrip = await createTrip(data)
    ElMessage.success('行程创建成功，已自动生成搭配')
    viewTrip(newTrip.id)
  }
  dialogVisible.value = false
}

const handleDelete = async () => {
  if (!currentTrip.value) return
  await ElMessageBox.confirm(`确定删除「${currentTrip.value.name}」吗？`, '提示', { type: 'warning' })
  await deleteTrip(currentTrip.value.id)
  ElMessage.success('已删除')
  currentTrip.value = null
  loadTrips()
}

const handleRegenerate = async () => {
  if (!currentTrip.value) return
  await ElMessageBox.confirm('重新生成将清空当前打包进度，确定继续？', '提示', { type: 'warning' })
  await regenerateTrip(currentTrip.value.id)
  ElMessage.success('已重新生成搭配清单')
  viewTrip(currentTrip.value.id)
}

const handleTogglePack = async (item) => {
  await togglePackItem(item.id)
  viewTrip(currentTrip.value.id)
}

const handlePackAll = async () => {
  if (!currentTrip.value) return
  await packAllItems(currentTrip.value.id)
  ElMessage.success('已全部标记为已打包')
  viewTrip(currentTrip.value.id)
}

const handleSaveDayFavorite = async (day) => {
  if (!currentTrip.value) return
  const fav = await saveTripFavorite(currentTrip.value.id, { day_id: day.id })
  ElMessage.success(`已收藏为「${fav.name}」，可在场合收藏中查看`)
}

const handleExport = async () => {
  if (!currentTrip.value) return
  const result = await exportTrip(currentTrip.value.id)
  exportContent.value = result.content
  exportVisible.value = true
}

const copyExport = async () => {
  try {
    await navigator.clipboard.writeText(exportContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动选择复制')
  }
}

const downloadExport = () => {
  const blob = new Blob([exportContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentTrip.value?.name || '行程'}_打包清单.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const handleViewTrip = (e) => {
  const id = e.detail?.id
  if (!id) return
  if (!trips.value.length) {
    loadTrips().then(() => {
      const trip = trips.value.find(t => t.id === id)
      if (trip) viewTrip(trip)
    })
  } else {
    const trip = trips.value.find(t => t.id === id)
    if (trip) viewTrip(trip)
    else {
      getTrip(id).then(data => {
        currentTrip.value = data
      })
    }
  }
}

onMounted(() => {
  loadMeta()
  loadTrips()
  window.addEventListener('view-trip', handleViewTrip)
})

onUnmounted(() => {
  window.removeEventListener('view-trip', handleViewTrip)
})
</script>

<style scoped>
.trip-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.trip-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.trip-card:hover {
  box-shadow: 0 4px 20px rgba(74, 44, 42, 0.12);
  transform: translateY(-2px);
}

.trip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.trip-name {
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
}

.trip-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.meta-item .el-icon {
  color: #c9a96e;
}

.trip-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.trip-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f0e8dd;
  margin-top: auto;
}

.back-bar {
  margin-bottom: 16px;
}

.trip-overview .ov-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.ov-title {
  font-size: 22px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 6px;
}

.ov-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.ov-meta .el-icon {
  color: #c9a96e;
}

.ov-meta .sep {
  color: #ccc;
  margin: 0 4px;
}

.ov-actions {
  display: flex;
  gap: 8px;
}

.stat-cards-mini {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.stat-card-mini {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #faf7f5;
  border-radius: 10px;
}

.scm-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.scm-value {
  font-size: 18px;
  font-weight: 700;
  color: #4a2c2a;
  line-height: 1.2;
}

.scm-label {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.ov-actions-row {
  display: flex;
  gap: 10px;
}

.trip-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.day-card {
  margin-bottom: 16px;
}

.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}

.day-title {
  display: flex;
  align-items: center;
}

.day-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #c9a96e, #e8c87a);
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  margin-right: 12px;
}

.day-date {
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
}

.section-subtitle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #4a2c2a;
  margin: 14px 0 10px;
}

.pieces-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.piece-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #faf7f5;
  border-radius: 10px;
  border: 2px solid transparent;
  transition: all 0.2s;
  flex: 1;
  min-width: 180px;
}

.piece-card.packed {
  opacity: 0.65;
}

.piece-card.packed::after {
  content: '已打包';
  position: absolute;
  top: 6px;
  right: 6px;
  font-size: 10px;
  background: #6ba878;
  color: #fff;
  padding: 1px 6px;
  border-radius: 8px;
}

.piece-card.spare {
  background: #fff8ef;
}

.pc-checkbox {
  cursor: pointer;
}

.pc-photo {
  width: 50px;
  height: 50px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pc-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pc-empty {
  color: #ccc;
}

.pc-info {
  flex: 1;
  min-width: 0;
}

.pc-cat {
  font-size: 11px;
  color: #c9a96e;
  font-weight: 600;
}

.pc-name {
  font-size: 13px;
  font-weight: 600;
  color: #4a2c2a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pc-tags {
  font-size: 11px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
}

.pc-reuse {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  color: #6ba878;
  background: #eaf3eb;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.reason-box {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  background: #faf7f5;
  border-radius: 10px;
  font-size: 13px;
  color: #666;
  margin-top: 12px;
  align-items: flex-start;
}

.reason-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reason-item {
  line-height: 1.6;
}

.storage-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.storage-card {
  border: 1px solid #f0e8dd;
  border-radius: 10px;
  overflow: hidden;
}

.storage-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #faf7f5;
  font-weight: 600;
  color: #4a2c2a;
}

.storage-name {
  flex: 1;
}

.storage-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  padding: 14px 16px;
}

.storage-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.si-photo {
  width: 36px;
  height: 36px;
  background: #f5efe6;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.si-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.si-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.si-meta {
  font-size: 11px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 10px;
  border-left: 4px solid #ccc;
  background: #faf7f5;
}

.risk-card.risk-高 {
  background: #fdf2f0;
  border-left-color: #c83c3c;
}

.risk-card.risk-中 {
  background: #fff8ef;
  border-left-color: #e8a45b;
}

.risk-card.risk-低 {
  background: #f0f7f1;
  border-left-color: #6ba878;
}

.risk-badge {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.badge-高 {
  background: #c83c3c;
  color: #fff;
}

.badge-中 {
  background: #e8a45b;
  color: #fff;
}

.badge-低 {
  background: #6ba878;
  color: #fff;
}

.risk-info {
  flex: 1;
}

.ri-name {
  font-size: 14px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 4px;
}

.ri-meta {
  font-size: 12px;
  color: #888;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ri-meta .sep {
  color: #ccc;
  margin: 0 4px;
}

.ri-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #8b6f47;
  line-height: 1.6;
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

.export-content {
  background: #faf7f5;
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow: auto;
}

.export-content pre {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', monospace;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  color: #4a2c2a;
}

@media (max-width: 768px) {
  .pieces-row {
    flex-direction: column;
  }
  .piece-card {
    min-width: auto;
  }
}
</style>
