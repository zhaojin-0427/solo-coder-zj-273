<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><WarningFilled /></el-icon>
      异常处理
      <el-button class="btn-primary" style="margin-left: auto;" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增异常
      </el-button>
    </div>

    <div class="stat-cards">
      <StatCard
        :icon="Warning"
        :value="pendingCount"
        label="待处理异常"
        icon-color="#e8a45b,#f0c088"
      />
      <StatCard
        :icon="CircleCheck"
        :value="resolvedCount"
        label="已解决异常"
        icon-color="#6ba878,#8ac492"
      />
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-input v-model="searchText" placeholder="搜索饰品名称" clearable style="width: 200px;" @input="loadData">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filters.exception_type" placeholder="异常类型" clearable @change="loadData">
          <el-option v-for="t in meta.inventory_exception_types" :key="t" :label="t" :value="t" />
        </el-select>
        <el-select v-model="filters.resolved" placeholder="处理状态" clearable @change="loadData">
          <el-option label="未解决" :value="false" />
          <el-option label="已解决" :value="true" />
        </el-select>
        <el-button @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table :data="filteredList" stripe>
        <el-table-column label="饰品" min-width="200">
          <template #default="{ row }">
            <TablePhotoCell
              :photo="row.accessory?.photo"
              :name="row.accessory?.name"
              :category="row.accessory?.category"
              :color-family="row.accessory?.material"
              :size="44"
            />
          </template>
        </el-table-column>
        <el-table-column label="异常类型" width="120">
          <template #default="{ row }">
            <el-tag :type="exceptionTypeMap[row.exception_type]?.type || 'info'" effect="light">
              {{ row.exception_type || '未分类' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="描述" min-width="180" prop="description" show-overflow-tooltip />
        <el-table-column label="关联盘点批次" width="160" prop="batch_name" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.batch_name">{{ row.batch_name }}</span>
            <span v-else style="color: #999;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="上报日期" width="120">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 4px; color: #666; font-size: 13px;">
              <el-icon><Calendar /></el-icon>
              <DateDisplay :date="row.reported_at" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.resolved" type="success" effect="light">已解决</el-tag>
            <el-tag v-else type="danger" effect="light">未解决</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理人" width="120">
          <template #default="{ row }">
            <div v-if="row.handler" style="display: flex; align-items: center; gap: 4px; font-size: 13px;">
              <el-icon><User /></el-icon>
              {{ row.handler }}
            </div>
            <span v-else style="color: #999;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.resolved" size="small" type="success" @click="openResolveDialog(row)">
              <el-icon><CircleCheck /></el-icon> 解决
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="filteredList.length === 0" class="empty-tip" style="padding: 40px 20px;">
        <el-icon><WarningFilled /></el-icon>
        <p>暂无异常记录</p>
      </div>
    </div>

    <el-dialog v-model="resolveDialogVisible" title="解决异常" width="520px">
      <el-form :model="resolveForm" ref="resolveFormRef" :rules="resolveRules" label-width="100px">
        <el-form-item label="饰品">
          <span style="font-weight: 500; color: #4a2c2a;">{{ currentException?.accessory?.name }}</span>
        </el-form-item>
        <el-form-item label="异常类型">
          <el-tag :type="exceptionTypeMap[currentException?.exception_type]?.type || 'info'" effect="light">
            {{ currentException?.exception_type }}
          </el-tag>
        </el-form-item>
        <el-form-item label="解决方案" prop="resolution">
          <el-input v-model="resolveForm.resolution" type="textarea" :rows="3" placeholder="请输入解决方案" />
        </el-form-item>
        <el-form-item label="处理人" prop="handler">
          <el-input v-model="resolveForm.handler" placeholder="请输入处理人姓名" />
        </el-form-item>
        <el-form-item v-if="currentException?.exception_type === '缺失'" label="已找回">
          <el-checkbox v-model="resolveForm.found">标记该饰品已找回</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleResolve">确认解决</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createDialogVisible" title="新增异常" width="560px">
      <el-form :model="createForm" ref="createFormRef" :rules="createRules" label-width="100px">
        <el-form-item label="饰品" prop="accessory_id">
          <el-select v-model="createForm.accessory_id" placeholder="选择饰品" style="width: 100%;" filterable>
            <el-option
              v-for="acc in accessories" :key="acc.id" :label="acc.name" :value="acc.id">
              <span style="display: flex; align-items: center; gap: 8px;">
                <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
                {{ acc.name }}
                <span style="color: #999; font-size: 12px;">({{ acc.category }})</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="异常类型" prop="exception_type">
          <el-select v-model="createForm.exception_type" placeholder="选择异常类型" style="width: 100%;">
            <el-option v-for="t in meta.inventory_exception_types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联盘点批次">
          <el-select v-model="createForm.batch_id" placeholder="选择盘点批次（可选）" style="width: 100%;" clearable>
            <el-option v-for="b in batches" :key="b.id" :label="b.batch_name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入异常描述" />
        </el-form-item>
        <el-form-item label="上报日期" prop="reported_at">
          <el-date-picker v-model="createForm.reported_at" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  WarningFilled, Plus, CircleCheck, Delete, Refresh, Picture,
  Search, Calendar, User, Warning
} from '@element-plus/icons-vue'
import {
  getInventoryExceptions, resolveInventoryException, deleteInventoryException,
  createInventoryException, getAccessories, getMeta, getInventoryBatches
} from '@/api'
import StatCard from '@/components/common/StatCard.vue'
import TablePhotoCell from '@/components/common/TablePhotoCell.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'
import { colorMap } from '@/composables/useColorMap'

const meta = ref({ inventory_exception_types: [] })
const list = ref([])
const accessories = ref([])
const batches = ref([])
const searchText = ref('')
const filters = reactive({ exception_type: '', resolved: '' })

const exceptionTypeMap = {
  '缺失': { type: 'danger' },
  '损坏': { type: 'warning' },
  '证书不全': { type: 'info' },
  '位置不符': { type: 'warning' },
  '借出未登记': { type: 'primary' },
  '其他': { type: 'info' }
}

const pendingCount = computed(() => list.value.filter(e => !e.resolved).length)
const resolvedCount = computed(() => list.value.filter(e => e.resolved).length)

const filteredList = computed(() => {
  if (!searchText.value) return list.value
  const kw = searchText.value.toLowerCase()
  return list.value.filter(e => e.accessory?.name?.toLowerCase().includes(kw) || e.description?.toLowerCase().includes(kw))
})

const resolveDialogVisible = ref(false)
const currentException = ref(null)
const resolveFormRef = ref(null)
const resolveForm = reactive({ resolution: '', handler: '', found: false })
const resolveRules = {
  resolution: [{ required: true, message: '请输入解决方案', trigger: 'blur' }],
  handler: [{ required: true, message: '请输入处理人', trigger: 'blur' }]
}

const createDialogVisible = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  accessory_id: null, exception_type: '', batch_id: null, description: '', reported_at: '' })
const createRules = {
  accessory_id: [{ required: true, message: '请选择饰品', trigger: 'change' }],
  exception_type: [{ required: true, message: '请选择异常类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入异常描述', trigger: 'blur' }],
  reported_at: [{ required: true, message: '请选择上报日期', trigger: 'change' }]
}

const loadMeta = async () => {
  meta.value = await getMeta()
}

const loadData = async () => {
  const params = {}
  if (filters.exception_type) params.exception_type = filters.exception_type
  if (filters.resolved !== '' && filters.resolved !== null && filters.resolved !== undefined) {
    params.resolved = filters.resolved
  }
  list.value = await getInventoryExceptions(params)
}

const loadAccessories = async () => {
  accessories.value = await getAccessories()
}

const loadBatches = async () => {
  batches.value = await getInventoryBatches()
}

const openResolveDialog = (row) => {
  currentException.value = row
  resolveForm.resolution = ''
  resolveForm.handler = ''
  resolveForm.found = false
  resolveDialogVisible.value = true
}

const handleResolve = async () => {
  await resolveFormRef.value.validate()
  const data = {
    resolution: resolveForm.resolution,
    handler: resolveForm.handler
  }
  if (currentException.value.exception_type === '缺失') {
    data.found = resolveForm.found
  }
  await resolveInventoryException(currentException.value.id, data)
  ElMessage.success('异常已解决')
  resolveDialogVisible.value = false
  loadData()
}

const openCreateDialog = () => {
  Object.assign(createForm, {
    accessory_id: null, exception_type: '', batch_id: null, description: '', reported_at: new Date().toISOString().slice(0, 10)
  })
  createDialogVisible.value = true
}

const handleCreate = async () => {
  await createFormRef.value.validate()
  await createInventoryException(createForm)
  ElMessage.success('异常已创建')
  createDialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除这条异常记录吗？`, '提示', { type: 'warning' })
  await deleteInventoryException(row.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(() => {
  loadMeta()
  loadData()
  loadAccessories()
  loadBatches()
})
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}
</style>
