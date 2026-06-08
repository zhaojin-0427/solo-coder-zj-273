<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Files /></el-icon>
      证书档案
      <el-button class="btn-primary" style="margin-left: auto;" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加证书
      </el-button>
    </div>

    <div class="stat-cards">
      <StatCard
        :icon="Files"
        :value="stats.total"
        label="证书总数"
        icon-color="#c9a96e,#b8956a"
      />
      <StatCard
        :icon="Wallet"
        :value="stats.covered"
        label="有证书饰品"
        icon-color="#6ba878,#5a9a68"
      />
      <StatCard
        :icon="WarningFilled"
        :value="stats.missing"
        label="证书缺失"
        icon-color="#e8856a,#d4705a"
      />
      <StatCard
        :icon="TrendCharts"
        :value="stats.rate + '%'"
        label="证书覆盖率"
        icon-color="#7a9cd4,#6a8cc4"
      />
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-select v-model="filters.accessory_id" placeholder="选择饰品" clearable @change="loadData">
          <el-option v-for="a in accessories" :key="a.id" :label="a.name" :value="a.id" />
        </el-select>
        <el-select v-model="filters.cert_type" placeholder="证书类型" clearable @change="loadData">
          <el-option v-for="t in meta.cert_types" :key="t" :label="t" :value="t" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索证书编号/机构" clearable style="width: 220px;" @input="loadData">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div v-if="filteredList.length === 0" class="empty-tip">
        <el-icon><Files /></el-icon>
        <p>暂无证书记录，点击右上角添加</p>
      </div>

      <el-table v-else :data="filteredList" style="width: 100%">
        <el-table-column label="证书照片" width="120" align="center">
          <template #default="{ row }">
            <div class="cert-thumb" @click="handlePreview(row)">
              <img v-if="row.file_path" :src="'/uploads/' + row.file_path" :alt="row.file_name" />
              <div v-else class="thumb-placeholder">
                <el-icon :size="24"><Picture /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="饰品名称" prop="accessory.name" min-width="140">
          <template #default="{ row }">
            <span class="text-primary">{{ row.accessory ? row.accessory.name : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="证书类型" width="130">
          <template #default="{ row }">
            <el-tag :type="getCertTypeTag(row.cert_type)" effect="light" size="small">
              {{ row.cert_type || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="证书编号" prop="cert_number" min-width="140">
          <template #default="{ row }">
            {{ row.cert_number || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="签发机构" prop="issuer" min-width="140">
          <template #default="{ row }">
            {{ row.issuer || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="签发日期" prop="issue_date" width="120">
          <template #default="{ row }">
            <DateDisplay :date="row.issue_date" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="primary" link @click="openDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑证书' : '添加证书'" width="640px">
      <el-form :model="form" ref="formRef" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择饰品" prop="accessory_id">
              <el-select v-model="form.accessory_id" placeholder="选择饰品" style="width: 100%" filterable>
                <el-option v-for="a in accessories" :key="a.id" :label="a.name" :value="a.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证书类型" prop="cert_type">
              <el-select v-model="form.cert_type" placeholder="选择证书类型" style="width: 100%">
                <el-option v-for="t in meta.cert_types" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="证书文件">
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="true"
                :limit="1"
                :on-change="handleFileChange"
                :file-list="fileList"
                accept="image/*,.pdf"
              >
                <el-button><el-icon><Upload /></el-icon> 选择文件</el-button>
                <template #tip>
                  <div style="color: #999; font-size: 12px;">支持图片/PDF格式，不超过 16MB</div>
                </template>
              </el-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证书编号" prop="cert_number">
              <el-input v-model="form.cert_number" placeholder="请输入证书编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="签发日期" prop="issue_date">
              <el-date-picker v-model="form.issue_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="签发机构" prop="issuer">
              <el-input v-model="form.issuer" placeholder="请输入签发机构" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="请输入备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewVisible" title="证书详情" width="560px">
      <div v-if="viewData" class="view-content">
        <div class="view-image" v-if="viewData.file_path">
          <img :src="'/uploads/' + viewData.file_path" :alt="viewData.file_name" @click="handlePreview(viewData)" />
        </div>
        <div v-else class="view-image-placeholder">
          <el-icon :size="60"><Picture /></el-icon>
          <p>暂无证书图片</p>
        </div>
        <el-descriptions :column="2" border style="margin-top: 20px;">
          <el-descriptions-item label="饰品名称">{{ viewData.accessory ? viewData.accessory.name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="证书类型">
            <el-tag :type="getCertTypeTag(viewData.cert_type)" effect="light" size="small">
              {{ viewData.cert_type || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="证书编号">{{ viewData.cert_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="签发日期">
            <DateDisplay :date="viewData.issue_date" />
          </el-descriptions-item>
          <el-descriptions-item label="签发机构" :span="2">{{ viewData.issuer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ viewData.created_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ viewData.notes || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <el-dialog v-model="previewVisible" title="证书预览" width="720px">
      <div class="preview-wrap">
        <img v-if="previewUrl" :src="previewUrl" alt="证书预览" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Files, Plus, Edit, Delete, Picture, Upload, Search, View,
  Wallet, WarningFilled, TrendCharts
} from '@element-plus/icons-vue'
import {
  getMeta, getCertificates, createCertificate, updateCertificate, deleteCertificate,
  getAccessories
} from '@/api'
import StatCard from '@/components/common/StatCard.vue'
import DateDisplay from '@/components/common/DateDisplay.vue'

const meta = ref({ cert_types: [] })
const list = ref([])
const accessories = ref([])
const searchText = ref('')
const filters = reactive({ accessory_id: '', cert_type: '' })

const stats = computed(() => {
  const total = list.value.length
  const coveredIds = new Set(list.value.map(c => c.accessory_id))
  const covered = coveredIds.size
  const missing = accessories.value.length - covered
  const rate = accessories.value.length > 0 ? Math.round(covered / accessories.value.length * 100) : 0
  return { total, covered, missing, rate }
})

const getCertTypeTag = (type) => {
  const map = {
    '购买发票': 'success',
    '珠宝鉴定证书': 'primary',
    '品牌证书': 'warning',
    '保修卡': 'info',
    'GIA证书': 'primary',
    'NGTC证书': 'success',
    '其他': 'info'
  }
  return map[type] || 'info'
}

const filteredList = computed(() => {
  if (!searchText.value) return list.value
  const kw = searchText.value.toLowerCase()
  return list.value.filter(c =>
    (c.cert_number && c.cert_number.toLowerCase().includes(kw)) ||
    (c.issuer && c.issuer.toLowerCase().includes(kw))
  )
})

const dialogVisible = ref(false)
const viewVisible = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')
const viewData = ref(null)
const editing = ref(false)
const formRef = ref(null)
const fileObj = ref(null)
const fileList = ref([])

const defaultForm = () => ({
  id: null,
  accessory_id: '',
  cert_type: '',
  cert_number: '',
  issue_date: '',
  issuer: '',
  notes: ''
})
const form = reactive(defaultForm())

const rules = {
  accessory_id: [{ required: true, message: '请选择饰品', trigger: 'change' }],
  cert_type: [{ required: true, message: '请选择证书类型', trigger: 'change' }]
}

const loadMeta = async () => {
  const data = await getMeta()
  meta.value = data
}

const loadData = async () => {
  const params = {}
  Object.keys(filters).forEach(k => { if (filters[k]) params[k] = filters[k] })
  list.value = await getCertificates(params)
}

const loadAccessories = async () => {
  accessories.value = await getAccessories()
}

const openDialog = (cert) => {
  fileObj.value = null
  fileList.value = []
  if (cert) {
    editing.value = true
    Object.assign(form, {
      id: cert.id,
      accessory_id: cert.accessory_id,
      cert_type: cert.cert_type,
      cert_number: cert.cert_number,
      issue_date: cert.issue_date,
      issuer: cert.issuer,
      notes: cert.notes
    })
    if (cert.file_path) {
      fileList.value = [{ name: cert.file_name, url: '/uploads/' + cert.file_path }]
    }
  } else {
    editing.value = false
    Object.assign(form, defaultForm())
  }
  dialogVisible.value = true
}

const handleFileChange = (file) => {
  fileObj.value = file.raw
  fileList.value = [file]
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const fd = new FormData()
  Object.keys(form).forEach(k => {
    if (k === 'id') return
    fd.append(k, form[k] || '')
  })
  if (fileObj.value) {
    fd.append('file', fileObj.value)
  }

  if (editing.value) {
    await updateCertificate(form.id, fd)
    ElMessage.success('已更新')
  } else {
    await createCertificate(fd)
    ElMessage.success('已添加')
  }
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (cert) => {
  await ElMessageBox.confirm(`确定删除该证书吗？`, '提示', { type: 'warning' })
  await deleteCertificate(cert.id)
  ElMessage.success('已删除')
  loadData()
}

const handleView = (cert) => {
  viewData.value = cert
  viewVisible.value = true
}

const handlePreview = (cert) => {
  if (cert.file_path) {
    previewUrl.value = '/uploads/' + cert.file_path
    previewVisible.value = true
  } else {
    ElMessage.info('暂无证书文件')
  }
}

onMounted(() => {
  loadMeta()
  loadAccessories()
  loadData()
})
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.cert-thumb {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5efe6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.cert-thumb:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(74, 44, 42, 0.15);
}

.cert-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  color: #c9b8a0;
}

.text-primary {
  color: #4a2c2a;
  font-weight: 500;
}

.view-content {
  padding: 0 10px;
}

.view-image {
  width: 100%;
  max-height: 300px;
  background: #f5efe6;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-in;
}

.view-image img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.view-image-placeholder {
  width: 100%;
  height: 200px;
  background: #f5efe6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c9b8a0;
  gap: 8px;
}

.preview-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
}

.preview-wrap img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}
</style>
