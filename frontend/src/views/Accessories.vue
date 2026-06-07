<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><Collection /></el-icon>
      饰品目录
      <el-button class="btn-primary" style="margin-left: auto;" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加饰品
      </el-button>
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-select v-model="filters.category" placeholder="品类" clearable @change="loadData">
          <el-option v-for="c in meta.categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filters.color_family" placeholder="色系" clearable @change="loadData">
          <el-option v-for="c in meta.color_families" :key="c" :label="c" :value="c">
            <span class="color-dot" :style="{ background: colorMap[c] }"></span>{{ c }}
          </el-option>
        </el-select>
        <el-select v-model="filters.style" placeholder="风格" clearable @change="loadData">
          <el-option v-for="s in meta.styles" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="filters.occasion" placeholder="场合" clearable @change="loadData">
          <el-option v-for="o in meta.occasions" :key="o" :label="o" :value="o" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索名称" clearable style="width: 200px;" @input="loadData" />
      </div>

      <div v-if="filteredList.length === 0" class="empty-tip">
        <el-icon><Collection /></el-icon>
        <p>暂无饰品，点击右上角添加</p>
      </div>

      <div v-else class="card-grid">
        <div v-for="acc in filteredList" :key="acc.id" class="acc-card">
          <div class="acc-photo">
            <img v-if="acc.photo" :src="'/uploads/' + acc.photo" :alt="acc.name" />
            <div v-else class="photo-placeholder">
              <el-icon :size="40"><Picture /></el-icon>
            </div>
            <span class="acc-category">{{ acc.category }}</span>
          </div>
          <div class="acc-info">
            <h4 class="acc-name">{{ acc.name }}</h4>
            <div class="acc-meta">
              <span class="color-dot" :style="{ background: colorMap[acc.color_family] }"></span>
              <span>{{ acc.color }}</span>
              <span class="divider">·</span>
              <span>{{ acc.material }}</span>
            </div>
            <div class="acc-tags">
              <span class="tag-item">{{ acc.style }}</span>
              <span v-for="o in acc.occasions" :key="o" class="tag-item">{{ o }}</span>
            </div>
            <div class="acc-storage">
              <el-icon><Location /></el-icon>
              {{ acc.storage_location || '未标记位置' }}
            </div>
            <div class="acc-wear">
              <span>佩戴 {{ acc.wear_count }} 次</span>
              <span v-if="acc.last_worn_date">· 上次 {{ acc.last_worn_date }}</span>
            </div>
          </div>
          <div class="acc-actions">
            <el-button size="small" type="success" @click="handleWear(acc)">
              <el-icon><Check /></el-icon>佩戴
            </el-button>
            <el-button size="small" @click="openDialog(acc)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(acc)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑饰品' : '添加饰品'" width="640px">
      <el-form :model="form" ref="formRef" :rules="rules" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品类" prop="category">
              <el-select v-model="form.category" placeholder="选择品类" style="width: 100%">
                <el-option v-for="c in meta.categories" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材质" prop="material">
              <el-select v-model="form.material" placeholder="选择材质" style="width: 100%">
                <el-option v-for="m in meta.materials" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="色系" prop="color_family">
              <el-select v-model="form.color_family" placeholder="选择色系" style="width: 100%">
                <el-option v-for="c in meta.color_families" :key="c" :label="c" :value="c">
                  <span class="color-dot" :style="{ background: colorMap[c] }"></span>{{ c }}
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="具体颜色" prop="color">
              <el-input v-model="form.color" placeholder="如：亮金色、樱花粉" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风格" prop="style">
              <el-select v-model="form.style" placeholder="选择风格" style="width: 100%">
                <el-option v-for="s in meta.styles" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="佩戴场合">
              <el-select v-model="form.occasions" multiple placeholder="选择场合" style="width: 100%">
                <el-option v-for="o in meta.occasions" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="收纳位置">
              <el-input v-model="form.storage_location" placeholder="如：首饰盒A层" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上次佩戴">
              <el-date-picker v-model="form.last_worn_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="照片">
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="true"
                :limit="1"
                :on-change="handlePhotoChange"
                accept="image/*"
              >
                <el-button><el-icon><Upload /></el-icon> 选择图片</el-button>
                <template #tip>
                  <div style="color: #999; font-size: 12px;">支持 jpg/png 格式，不超过 16MB</div>
                </template>
              </el-upload>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMeta, getAccessories, createAccessory, updateAccessory, deleteAccessory, wearAccessory } from '@/api'

const meta = ref({ categories: [], materials: [], color_families: [], styles: [], occasions: [] })
const list = ref([])
const searchText = ref('')
const filters = reactive({ category: '', color_family: '', style: '', occasion: '' })

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const filteredList = computed(() => {
  if (!searchText.value) return list.value
  const kw = searchText.value.toLowerCase()
  return list.value.filter(a => a.name.toLowerCase().includes(kw))
})

const dialogVisible = ref(false)
const editing = ref(false)
const formRef = ref(null)
const photoFile = ref(null)

const defaultForm = () => ({
  id: null, name: '', category: '', material: '', color: '',
  color_family: '', style: '', occasions: [], storage_location: '',
  last_worn_date: '', wear_count: 0
})
const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择品类', trigger: 'change' }],
  material: [{ required: true, message: '请选择材质', trigger: 'change' }],
  color_family: [{ required: true, message: '请选择色系', trigger: 'change' }],
  color: [{ required: true, message: '请输入颜色', trigger: 'blur' }],
  style: [{ required: true, message: '请选择风格', trigger: 'change' }]
}

const loadMeta = async () => {
  meta.value = await getMeta()
}

const loadData = async () => {
  const params = {}
  Object.keys(filters).forEach(k => { if (filters[k]) params[k] = filters[k] })
  list.value = await getAccessories(params)
}

const openDialog = (acc) => {
  photoFile.value = null
  if (acc) {
    editing.value = true
    Object.assign(form, {
      id: acc.id, name: acc.name, category: acc.category, material: acc.material,
      color: acc.color, color_family: acc.color_family, style: acc.style,
      occasions: [...acc.occasions], storage_location: acc.storage_location,
      last_worn_date: acc.last_worn_date, wear_count: acc.wear_count
    })
  } else {
    editing.value = false
    Object.assign(form, defaultForm())
  }
  dialogVisible.value = true
}

const handlePhotoChange = (file) => {
  photoFile.value = file.raw
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const fd = new FormData()
  Object.keys(form).forEach(k => {
    if (k === 'id') return
    if (k === 'occasions') {
      fd.append(k, JSON.stringify(form[k]))
    } else {
      fd.append(k, form[k])
    }
  })
  if (photoFile.value) {
    fd.append('photo', photoFile.value)
  }

  if (editing.value) {
    await updateAccessory(form.id, fd)
    ElMessage.success('已更新')
  } else {
    await createAccessory(fd)
    ElMessage.success('已添加')
  }
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (acc) => {
  await ElMessageBox.confirm(`确定删除「${acc.name}」吗？`, '提示', { type: 'warning' })
  await deleteAccessory(acc.id)
  ElMessage.success('已删除')
  loadData()
}

const handleWear = async (acc) => {
  await wearAccessory(acc.id)
  ElMessage.success(`已记录佩戴「${acc.name}」`)
  loadData()
}

onMounted(() => {
  loadMeta()
  loadData()
})
</script>

<style scoped>
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.acc-card {
  border: 1px solid #f0e8dd;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.acc-card:hover {
  box-shadow: 0 4px 16px rgba(74, 44, 42, 0.1);
  transform: translateY(-2px);
}

.acc-photo {
  position: relative;
  height: 180px;
  background: #f5efe6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.acc-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: #ccc;
}

.acc-category {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(74, 44, 42, 0.8);
  color: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.acc-info {
  padding: 12px 14px;
  flex: 1;
}

.acc-name {
  font-size: 15px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 8px;
}

.acc-meta {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.acc-meta .divider {
  margin: 0 6px;
  color: #ccc;
}

.acc-tags {
  margin-bottom: 8px;
}

.acc-storage {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 6px;
}

.acc-wear {
  font-size: 12px;
  color: #999;
}

.acc-actions {
  padding: 10px 14px;
  border-top: 1px solid #f0e8dd;
  display: flex;
  gap: 6px;
}

.acc-actions .el-button {
  flex: 1;
}
</style>
