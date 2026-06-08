<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Present /></el-icon>
      盘点任务
      <el-button class="btn-primary" style="margin-left: auto;" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增盘点
      </el-button>
    </div>

    <div v-if="!currentBatch">
      <div v-if="batches.length === 0" class="card">
        <div class="empty-tip">
          <el-icon><Present /></el-icon>
          <p>暂无盘点任务，点击右上角创建新的盘点任务</p>
        </div>
      </div>

      <div v-else class="batch-list">
        <div v-for="batch in batches" :key="batch.id" class="batch-card">
          <div class="batch-header">
          </div>
          <div class="batch-info">
            <h4 class="batch-name">{{ batch.batch_name }}</h4>
            <el-tag :type="batchTypeMap[batch.batch_type]?.type || 'info'" size="small">
              {{ batchTypeMap[batch.batch_type]?.label || batch.batch_type }}
            </el-tag>
          </div>
          <div class="batch-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              周期：{{ batch.period || '未指定' }}
            </div>
            <div class="meta-item">
              <el-icon><Refresh /></el-icon>
              <DateDisplay :date="batch.start_date" /> ~ <DateDisplay :date="batch.end_date" />
            </div>
            <div class="meta-item">
              <StatusTag :status="batch.status" />
            </div>
          </div>
          <div class="batch-progress">
            <div class="progress-label">
              <span>盘点进度</span>
              <span>{{ batch.checked_count }}/{{ batch.total_count }}</span>
            </div>
            <el-progress
              :percentage="batch.completion_rate || 0"
              :color="'#c9a96e'"
              :stroke-width="8"
            />
          </div>
          <div class="batch-stats">
            <div class="stat-item">
              <el-icon color="#c83c3c"><Warning /></el-icon>
              <span>异常 {{ batch.exception_count }} 件</span>
            </div>
            <div class="batch-actions">
              <el-button size="small" type="primary" text @click="viewBatch(batch.id)">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </el-button>
              <el-button
                v-if="batch.status !== 'completed'"
                size="small"
                type="success"
                text
                @click.stop="handleComplete(batch)"
              >
                <el-icon><CircleCheck /></el-icon>
                完成盘点
              </el-button>
              <el-button size="small" type="danger" text @click.stop="handleDelete(batch)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else>
      <div class="back-bar">
        <el-button text @click="currentBatch = null; loadBatches()">
          <el-icon><ArrowLeft /></el-icon> 返回盘点列表
        </el-button>
      </div>

      <div class="card batch-detail">
        <div class="detail-header">
          <div>
            <h2 class="detail-title">{{ currentBatch.batch_name }}</h2>
            <div class="detail-meta">
              <el-tag :type="batchTypeMap[currentBatch.batch_type]?.type || 'info'" size="small">
                {{ batchTypeMap[currentBatch.batch_type]?.label || currentBatch.batch_type }}
              </el-tag>
              <StatusTag :status="currentBatch.status" size="small" />
              <span class="sep">·</span>
              <el-icon><Calendar /></el-icon>
              <DateDisplay :date="currentBatch.start_date" /> ~ {{ currentBatch.end_date || '进行中' }}
              <span class="sep">·</span>
              <el-icon><Present /></el-icon>
              周期：{{ currentBatch.period || '未指定' }}
              <span class="sep">·</span>
              操作人：{{ currentBatch.operator || '未指定' }}
            </div>
          </div>
          <div class="detail-actions">
            <el-button
              v-if="currentBatch.status !== 'completed'"
              size="small"
              class="btn-primary"
              @click="handleComplete(currentBatch)"
            >
              <el-icon><CircleCheck /></el-icon>
              完成盘点
            </el-button>
          </div>
        </div>

        <div class="stat-cards-mini">
          <StatCard
            :icon="Present"
            :value="currentBatch.checked_count + '/' + currentBatch.total_count"
            label="已盘点/总数"
            icon-color="#c9a96e,#e8c87a"
          />
          <StatCard
            :icon="Warning"
            :value="currentBatch.exception_count"
            label="异常数量"
            icon-color="#c83c3c,#e86b6b"
          />
          <StatCard
            :icon="CircleCheck"
            :value="currentBatch.total_count - currentBatch.exception_count - (currentBatch.total_count - currentBatch.checked_count)"
            label="正常在库"
            icon-color="#6ba878,#8ac492"
          />
          <StatCard
            :icon="Search"
            :value="currentBatch.total_count - currentBatch.checked_count"
            label="待盘点"
            icon-color="#999,#bbb"
          />
        </div>
      </div>

      <div class="card">
        <div class="section-title">
          <el-icon color="#c9a96e"><Collection /></el-icon>
          饰品盘点清单
          <div style="margin-left: auto; display: flex; gap: 10px;">
            <el-select v-model="itemFilter" size="small" style="width: 140px;">
              <el-option label="全部" value="" />
              <el-option label="待盘点" value="pending" />
              <el-option label="已盘点" value="checked" />
              <el-option label="异常" value="exception" />
            </el-select>
          </div>
        </div>
        <div v-if="filteredItems.length === 0" class="empty-tip" style="padding: 30px;">
          <el-icon><Collection /></el-icon>
          <p>暂无符合条件的饰品</p>
        </div>
        <div v-else class="item-list">
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="item-card"
            :class="{ 'item-exception': item.status === 'exception', 'item-checked': item.status === 'checked' }"
          >
            <div class="item-photo">
              <img v-if="item.accessory?.photo" :src="'/uploads/' + item.accessory.photo" :alt="item.accessory?.name" />
              <div v-else class="photo-placeholder">
                <el-icon :size="32"><Picture /></el-icon>
              </div>
              <el-tag
                v-if="item.status === 'checked'" type="success" size="small" effect="dark" class="item-status-tag">
                <el-icon><CircleCheck /></el-icon>
              </el-tag>
              <el-tag
                v-else-if="item.status === 'exception'" type="danger" size="small" effect="dark" class="item-status-tag">
                <el-icon><WarningFilled /></el-icon>
              </el-tag>
              <el-tag v-else type="info" size="small" effect="dark" class="item-status-tag">
                待盘点
              </el-tag>
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.accessory?.name || '未知饰品' }}</div>
              <div class="item-meta">
                <span>{{ item.accessory?.category || '-' }}</span>
                <span class="sep">·</span>
                <span>{{ item.accessory?.material || '-' }}</span>
              </div>
              <div class="item-location">
                <el-icon><Location /></el-icon>
                收纳位置：{{ item.expected_location || '未标记' }}
              </div>
              <div class="item-check-method">
                确认方式：{{ item.check_method === 'scan' ? '扫码' : '手动' }}
                <span v-if="item.checked_at" class="sep">·</span>
                <DateDisplay v-if="item.checked_at" :date="item.checked_at" />
              </div>
            </div>
            <div class="item-actions">
              <el-button
                v-if="item.status !== 'checked'"
                size="small"
                type="success"
                :disabled="currentBatch.status === 'completed'"
                @click="handleCheckItem(item)"
              >
                <el-icon><CircleCheck /></el-icon>
                确认在库
              </el-button>
              <el-button
                v-if="item.status !== 'exception'"
                size="small"
                type="danger"
                :disabled="currentBatch.status === 'completed'"
                @click="openExceptionDialog(item)"
              >
                <el-icon><WarningFilled /></el-icon>
                标记异常
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="createDialogVisible" title="新增盘点" width="560px">
      <el-form :model="createForm" ref="createFormRef" :rules="createRules" label-width="100px">
        <el-form-item label="批次名称" prop="batch_name">
          <el-input v-model="createForm.batch_name" placeholder="请输入批次名称" />
        </el-form-item>
        <el-form-item label="盘点类型" prop="batch_type">
          <el-select v-model="createForm.batch_type" placeholder="选择盘点类型" style="width: 100%;">
            <el-option
              v-for="t in meta.inventory_batch_types"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="盘点周期" prop="period">
          <el-input v-model="createForm.period" placeholder="如：2024年度、Q1、6月" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="createForm.start_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="createForm.operator" placeholder="请输入操作人姓名" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.notes" type="textarea" :rows="2" placeholder="备注信息..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleCreateBatch">
          <el-icon><Plus /></el-icon>
          创建盘点
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exceptionDialogVisible" title="标记异常" width="500px">
      <el-form :model="exceptionForm" ref="exceptionFormRef" :rules="exceptionRules" label-width="100px">
        <el-form-item label="饰品名称">
          <el-input :model-value="currentExceptionItem?.accessory?.name" disabled />
        </el-form-item>
        <el-form-item label="异常类型" prop="exception_type">
          <el-select v-model="exceptionForm.exception_type" placeholder="选择异常类型" style="width: 100%;">
            <el-option
              v-for="t in meta.inventory_exception_types"
              :key="t"
              :label="t"
              :value="t"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="exceptionForm.description" type="textarea" :rows="3" placeholder="请描述异常情况..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exceptionDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleCreateException">
          <el-icon><WarningFilled /></el-icon>
          确认标记异常
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Present, Plus, Edit, Delete, CircleCheck, WarningFilled, Refresh, Picture,
  Location, Search, Calendar, Box, View, ArrowRight, ArrowLeft, Warning, Collection
} from '@element-plus/icons-vue'
import {
  getMeta,
  getInventoryBatches, getInventoryBatch, createInventoryBatch,
  completeInventoryBatch, deleteInventoryBatch, checkInventoryItem,
  createInventoryException
} from '@/api'
import StatCard from '@/components/common/StatCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'
import { colorMap } from '@/composables/useColorMap'

const meta = ref({
  inventory_batch_types: [],
  inventory_exception_types: []
})
const batches = ref([])
const currentBatch = ref(null)
const itemFilter = ref('')

const createDialogVisible = ref(false)
const createFormRef = ref(null)
const exceptionDialogVisible = ref(false)
const exceptionFormRef = ref(null)
const currentExceptionItem = ref(null)

const batchTypeMap = {
  annual: { label: '年度盘点', type: 'warning' },
  quarterly: { label: '季度盘点', type: 'primary' },
  monthly: { label: '月度盘点', type: 'success' },
  temporary: { label: '临时盘点', type: 'info' }
}

const defaultCreateForm = () => ({
  batch_name: '',
  batch_type: '',
  period: '',
  start_date: '',
  operator: '',
  notes: ''
})
const createForm = reactive(defaultCreateForm())

const createRules = {
  batch_name: [{ required: true, message: '请输入批次名称', trigger: 'blur' }],
  batch_type: [{ required: true, message: '请选择盘点类型', trigger: 'change' }],
  period: [{ required: true, message: '请输入盘点周期', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

const defaultExceptionForm = () => ({
  exception_type: '',
  description: ''
})
const exceptionForm = reactive(defaultExceptionForm())

const exceptionRules = {
  exception_type: [{ required: true, message: '请选择异常类型', trigger: 'change' }]
}

const filteredItems = computed(() => {
  if (!currentBatch.value?.items) return []
  if (!itemFilter.value) return currentBatch.value.items
  return currentBatch.value.items.filter(i => i.status === itemFilter.value)
})

const loadMeta = async () => {
  meta.value = await getMeta()
}

const loadBatches = async () => {
  batches.value = await getInventoryBatches()
}

const viewBatch = async (id) => {
  currentBatch.value = await getInventoryBatch(id)
}

const openCreateDialog = () => {
  Object.assign(createForm, defaultCreateForm())
  createDialogVisible.value = true
}

const handleCreateBatch = async () => {
  await createFormRef.value.validate()
  const data = {
    batch_name: createForm.batch_name,
    batch_type: createForm.batch_type,
    period: createForm.period,
    start_date: createForm.start_date,
    operator: createForm.operator,
    notes: createForm.notes
  }
  await createInventoryBatch(data)
  ElMessage.success('盘点批次创建成功')
  createDialogVisible.value = false
  loadBatches()
}

const handleComplete = async (batch) => {
  ElMessageBox.confirm(
    `确定完成「${batch.batch_name}」吗？完成后将无法继续修改盘点结果。`,
    '提示',
    { type: 'warning' }
  ).then(async () => {
    await completeInventoryBatch(batch.id)
    ElMessage.success('盘点已完成')
    if (currentBatch.value && currentBatch.value.id === batch.id) {
      viewBatch(batch.id)
    } else {
      loadBatches()
    }
  }).catch(() => {})
}

const handleDelete = async (batch) => {
  ElMessageBox.confirm(
    `确定删除「${batch.batch_name}」吗？`,
    '提示',
    { type: 'warning' }
  ).then(async () => {
    await deleteInventoryBatch(batch.id)
    ElMessage.success('已删除')
    loadBatches()
  }).catch(() => {})
}

const handleCheckItem = async (item) => {
  await checkInventoryItem(item.id, { status: 'checked', check_method: 'manual' })
  ElMessage.success('已确认在库')
  if (currentBatch.value) {
    viewBatch(currentBatch.value.id)
  }
}

const openExceptionDialog = (item) => {
  currentExceptionItem.value = item
  Object.assign(exceptionForm, defaultExceptionForm())
  exceptionDialogVisible.value = true
}

const handleCreateException = async () => {
  await exceptionFormRef.value.validate()
  const data = {
    batch_id: currentExceptionItem.value.batch_id,
    accessory_id: currentExceptionItem.value.accessory_id,
    exception_type: exceptionForm.exception_type,
    description: exceptionForm.description
  }
  await createInventoryException(data)
  ElMessage.success('已标记异常')
  exceptionDialogVisible.value = false
  if (currentBatch.value) {
    viewBatch(currentBatch.value.id)
  }
}

onMounted(() => {
  loadMeta()
  loadBatches()
})
</script>

<style scoped>
.batch-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.batch-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.batch-card:hover {
  box-shadow: 0 4px 20px rgba(74, 44, 42, 0.12);
  transform: translateY(-2px);
}

.batch-header {
  margin-bottom: 10px;
}

.batch-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.batch-name {
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
  margin: 0;
}

.batch-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
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

.batch-progress {
  margin-bottom: 12px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.batch-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f0e8dd;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.batch-actions {
  display: flex;
  gap: 4px;
}

.back-bar {
  margin-bottom: 16px;
}

.batch-detail .detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-title {
  font-size: 22px;
  font-weight: 600;
  color: #4a2c2a;
  margin: 0 0 6px 0;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.detail-meta .el-icon {
  color: #c9a96e;
}

.detail-meta .sep {
  color: #ccc;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.stat-cards-mini {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 16px;
}

.item-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 14px;
}

.item-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: #faf7f5;
  border-radius: 10px;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.item-card:hover {
  border-color: #e8ddcc;
}

.item-card.item-checked {
  background: #f0f7f1;
}

.item-card.item-exception {
  background: #fdf2f0;
}

.item-photo {
  position: relative;
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: #ccc;
}

.item-status-tag {
  position: absolute;
  top: 6px;
  right: 6px;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.item-name {
  font-size: 15px;
  font-weight: 600;
  color: #4a2c2a;
}

.item-meta {
  font-size: 12px;
  color: #888;
}

.item-meta .sep {
  margin: 0 4px;
  color: #ccc;
}

.item-location {
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-location .el-icon {
  color: #c9a96e;
}

.item-check-method {
  font-size: 12px;
  color: #999;
}

.item-check-method .sep {
  margin: 0 4px;
  color: #ccc;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
}
</style>
