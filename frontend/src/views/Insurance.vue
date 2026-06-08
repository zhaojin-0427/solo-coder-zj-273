<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Wallet /></el-icon>
      保险清单
      <el-button class="btn-primary" style="margin-left: auto;" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        新增保险
      </el-button>
      <el-button @click="handleExport">
        <el-icon><Download /></el-icon>
        导出保险清单
      </el-button>
    </div>

    <div class="stat-cards">
      <StatCard
        :icon="Picture"
        :value="stats.totalAccessories || 0"
        label="饰品总数"
        icon-color="#c9a96e,#e8c87a"
      />
      <StatCard
        :icon="Wallet"
        :value="stats.insuredCount || 0"
        label="已投保数量"
        icon-color="#6ba878,#8ac492"
      />
      <StatCard
        :icon="Warning"
        :value="stats.uninsuredCount || 0"
        label="未投保数量"
        icon-color="#e8a45b,#f0c088"
      />
      <StatCard
        :icon="Money"
        :value="formatAmount(stats.currentTotalCoverage, '¥', 0)"
        label="当前总保额"
        icon-color="#5a8cc8,#7aa8e0"
      />
      <StatCard
        :icon="Notebook"
        :value="formatAmount(stats.suggestedTotalCoverage, '¥', 0)"
        label="建议总保额"
        icon-color="#9b7ab8,#b598d0"
      />
    </div>

    <div v-if="highValueUninsured.length > 0" class="card warning-card">
      <div class="section-title">
        <el-icon style="color: #c83c3c;"><Warning /></el-icon>
        高价值未投保饰品提醒
        <el-tag type="danger" effect="light" style="margin-left: 10px;">
          {{ highValueUninsured.length }} 件估值 ≥ ¥3,000 未投保
        </el-tag>
      </div>
      <el-table :data="highValueUninsured" stripe size="small">
        <el-table-column label="饰品" min-width="200">
          <template #default="{ row }">
            <TablePhotoCell
              :photo="row.photo"
              :name="row.name"
              :category="row.category"
              :color-family="row.material"
            />
          </template>
        </el-table-column>
        <el-table-column label="当前估值" width="140" align="center">
          <template #default="{ row }">
            <AmountDisplay :amount="row.current_value" color="#c83c3c" :font-weight="600" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button size="small" class="btn-primary" @click="openDialogForAccessory(row)">
              <el-icon><Plus /></el-icon>
              投保
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="card">
      <div class="section-title">保险列表</div>
      <div v-if="insuranceList.length === 0" class="empty-tip">
        <el-icon><Wallet /></el-icon>
        <p>暂无保险记录，点击右上角新增</p>
      </div>
      <el-table v-else :data="insuranceList" stripe>
        <el-table-column label="饰品照片" width="90" align="center">
          <template #default="{ row }">
            <div class="table-photo-small">
              <img v-if="row.accessory?.photo" :src="'/uploads/' + row.accessory.photo" />
              <el-icon v-else color="#ccc"><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="饰品名称" min-width="160">
          <template #default="{ row }">
            {{ row.accessory?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="当前估值" width="120" align="center">
          <template #default="{ row }">
            <AmountDisplay :amount="row.accessory?.current_value" />
          </template>
        </el-table-column>
        <el-table-column label="保险公司" prop="insurance_company" width="140" />
        <el-table-column label="保单号" prop="policy_number" width="160" />
        <el-table-column label="保额" width="120" align="center">
          <template #default="{ row }">
            <AmountDisplay :amount="row.coverage_amount" color="#8b6f47" :font-weight="600" />
          </template>
        </el-table-column>
        <el-table-column label="保费" width="100" align="center">
          <template #default="{ row }">
            <AmountDisplay :amount="row.premium" />
          </template>
        </el-table-column>
        <el-table-column label="生效日期" width="120" align="center">
          <template #default="{ row }">
            <DateDisplay :date="row.effective_date" />
          </template>
        </el-table-column>
        <el-table-column label="到期日期" width="120" align="center">
          <template #default="{ row }">
            <DateDisplay :date="row.expiry_date" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]" effect="light">
              {{ statusLabelMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑保险' : '新增保险'" width="640px">
      <el-form :model="form" ref="formRef" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="选择饰品" prop="accessory_id">
              <el-select v-model="form.accessory_id" placeholder="选择饰品" style="width: 100%" filterable>
                <el-option
                  v-for="acc in accessories"
                  :key="acc.id"
                  :label="acc.name + ' (估值: ¥' + formatAmount(acc.current_value, '', 0) + ')'"
                  :value="acc.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保险公司" prop="insurance_company">
              <el-select v-model="form.insurance_company" placeholder="选择保险公司" style="width: 100%">
                <el-option
                  v-for="c in meta.insurance_companies"
                  :key="c"
                  :label="c"
                  :value="c"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保单号" prop="policy_number">
              <el-input v-model="form.policy_number" placeholder="请输入保单号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保额" prop="coverage_amount">
              <el-input-number
                v-model="form.coverage_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入保额"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保费" prop="premium">
              <el-input-number
                v-model="form.premium"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入保费"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生效日期" prop="effective_date">
              <el-date-picker
                v-model="form.effective_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                placeholder="选择生效日期"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期日期" prop="expiry_date">
              <el-date-picker
                v-model="form.expiry_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                placeholder="选择到期日期"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
                <el-option label="有效" value="active" />
                <el-option label="过期" value="expired" />
                <el-option label="待续保" value="renewal" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model="form.remarks"
                type="textarea"
                :rows="3"
                placeholder="请输入备注信息"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmit">
          <el-icon><Refresh /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exportDialogVisible" title="导出保险清单" width="720px">
      <div class="export-content">
        <pre>{{ exportContent }}</pre>
      </div>
      <template #footer>
        <el-button @click="exportDialogVisible = false">关闭</el-button>
        <el-button class="btn-primary" @click="copyExportContent">
          <el-icon><Notebook /></el-icon>
          复制内容
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Wallet, Plus, Edit, Delete, Download, Coin, WarningFilled, Picture, Refresh, Notebook, Warning, Money
} from '@element-plus/icons-vue'
import {
  getInsuranceItems, createInsuranceItem, updateInsuranceItem, deleteInsuranceItem,
  exportInsuranceList, getAccessories, calculateValuation, getMeta
} from '@/api'
import StatCard from '@/components/common/StatCard.vue'
import TablePhotoCell from '@/components/common/TablePhotoCell.vue'
import AmountDisplay from '@/components/common/AmountDisplay.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'
import { useFormat } from '@/composables/useFormat'

const { formatAmount, formatDate } = useFormat()

const meta = ref({ insurance_companies: [] })
const insuranceList = ref([])
const accessories = ref([])
const exportDialogVisible = ref(false)
const exportContent = ref('')

const statusLabelMap = {
  active: '有效',
  expired: '过期',
  renewal: '待续保'
}

const statusTypeMap = {
  active: 'success',
  expired: 'danger',
  renewal: 'warning'
}

const stats = computed(() => {
  const total = accessories.value.length
  const insuredIds = new Set(insuranceList.value
    .filter(i => i.status === 'active')
    .map(i => i.accessory_id))
  const insuredCount = insuredIds.size
  const uninsuredCount = total - insuredCount
  const currentTotalCoverage = insuranceList.value
    .filter(i => i.status === 'active')
    .reduce((sum, i) => sum + (Number(i.coverage_amount) || 0), 0)
  const suggestedTotalCoverage = accessories.value
    .reduce((sum, a) => sum + (Number(a.current_value) || 0), 0)
  return {
    totalAccessories: total,
    insuredCount,
    uninsuredCount,
    currentTotalCoverage,
    suggestedTotalCoverage
  }
})

const highValueUninsured = computed(() => {
  const insuredIds = new Set(insuranceList.value
    .filter(i => i.status === 'active')
    .map(i => i.accessory_id))
  return accessories.value.filter(a => {
    const val = Number(a.current_value) || 0
    return val >= 3000 && !insuredIds.has(a.id)
  })
})

const dialogVisible = ref(false)
const editing = ref(false)
const formRef = ref(null)

const defaultForm = () => ({
  id: null,
  accessory_id: null,
  insurance_company: '',
  policy_number: '',
  coverage_amount: null,
  premium: null,
  effective_date: '',
  expiry_date: '',
  status: 'active',
  remarks: ''
})
const form = reactive(defaultForm())

const rules = {
  accessory_id: [{ required: true, message: '请选择饰品', trigger: 'change' }],
  insurance_company: [{ required: true, message: '请选择保险公司', trigger: 'change' }],
  policy_number: [{ required: true, message: '请输入保单号', trigger: 'blur' }],
  coverage_amount: [{ required: true, message: '请输入保额', trigger: 'blur' }],
  premium: [{ required: true, message: '请输入保费', trigger: 'blur' }],
  effective_date: [{ required: true, message: '请选择生效日期', trigger: 'change' }],
  expiry_date: [{ required: true, message: '请选择到期日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const loadMeta = async () => {
  const data = await getMeta()
  meta.value = data
}

const loadInsuranceData = async () => {
  const list = await getInsuranceItems()
  insuranceList.value = list.map(item => ({
    ...item,
    effective_date: item.effective_date || item.start_date || '',
    expiry_date: item.expiry_date || item.end_date || '',
    remarks: item.remarks || item.notes || ''
  }))
}

const loadAccessories = async () => {
  const list = await getAccessories()
  const accWithValuation = []
  for (const acc of list) {
    try {
      const val = await calculateValuation(acc.id)
      accWithValuation.push({ ...acc, current_value: val.current_value || acc.purchase_price || 0 })
    } catch {
      accWithValuation.push({ ...acc, current_value: acc.purchase_price || 0 })
    }
  }
  accessories.value = accWithValuation
}

const openDialog = (item) => {
  if (item) {
    editing.value = true
    Object.assign(form, {
      id: item.id,
      accessory_id: item.accessory_id,
      insurance_company: item.insurance_company,
      policy_number: item.policy_number,
      coverage_amount: item.coverage_amount,
      premium: item.premium,
      effective_date: item.effective_date || item.start_date || '',
      expiry_date: item.expiry_date || item.end_date || '',
      status: item.status,
      remarks: item.remarks || item.notes || ''
    })
  } else {
    editing.value = false
    Object.assign(form, defaultForm())
  }
  dialogVisible.value = true
}

const openDialogForAccessory = (acc) => {
  editing.value = false
  Object.assign(form, defaultForm())
  form.accessory_id = acc.id
  form.coverage_amount = acc.current_value || null
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const payload = {
    accessory_id: form.accessory_id,
    insurance_company: form.insurance_company,
    policy_number: form.policy_number,
    coverage_amount: form.coverage_amount,
    premium: form.premium,
    start_date: form.effective_date,
    end_date: form.expiry_date,
    status: form.status,
    notes: form.remarks
  }
  if (editing.value) {
    await updateInsuranceItem(form.id, payload)
    ElMessage.success('已更新')
  } else {
    await createInsuranceItem(payload)
    ElMessage.success('已添加')
  }
  dialogVisible.value = false
  loadInsuranceData()
}

const handleDelete = async (item) => {
  await ElMessageBox.confirm(
    `确定删除「${item.accessory?.name || item.policy_number}」的保险记录吗？`,
    '提示',
    { type: 'warning' }
  )
  await deleteInsuranceItem(item.id)
  ElMessage.success('已删除')
  loadInsuranceData()
}

const handleExport = async () => {
  try {
    exportContent.value = await exportInsuranceList()
    exportDialogVisible.value = true
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const copyExportContent = async () => {
  try {
    await navigator.clipboard.writeText(exportContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

onMounted(() => {
  loadMeta()
  loadInsuranceData()
  loadAccessories()
})
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.warning-card {
  border: 1px solid #f5d0d0;
  background: linear-gradient(135deg, #fff5f5 0%, #fff 100%);
}

.table-photo-small {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background: #f5efe6;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.table-photo-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.export-content {
  background: #faf7f5;
  border: 1px solid #f0e8dd;
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.export-content pre {
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #4a2c2a;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>
