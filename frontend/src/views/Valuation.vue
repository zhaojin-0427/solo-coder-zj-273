<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><TrendCharts /></el-icon>
      估值总览
      <el-button class="btn-primary" style="margin-left: auto;" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #c9a96e, #e8c87a);">
          <el-icon :size="22" color="#fff"><Coin /></el-icon>
        </div>
        <div>
          <div class="stat-v">¥{{ formatNumber(overview.total_valuation) }}</div>
          <div class="stat-l">资产总估值</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
          <el-icon :size="22" color="#fff"><Goods /></el-icon>
        </div>
        <div>
          <div class="stat-v">¥{{ formatNumber(overview.total_purchase_price) }}</div>
          <div class="stat-l">总购买价</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #e8a45b, #f0c088);">
          <el-icon :size="22" color="#fff"><Histogram /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ overview.depreciation_rate || 0 }}%</div>
          <div class="stat-l">整体折旧率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #6ba878, #8ac492);">
          <el-icon :size="22" color="#fff"><PieChart /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ overview.accessory_count || 0 }}</div>
          <div class="stat-l">饰品数量</div>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">估值趋势</div>
          <div ref="trendChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="card">
          <div class="section-title">品类价值分布</div>
          <div ref="categoryChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="card">
          <div class="section-title">风险等级价值分布</div>
          <div ref="riskChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <div class="card">
      <div class="section-title" style="display: flex; align-items: center; justify-content: space-between;">
        <span>高价值饰品列表</span>
        <el-tag size="small" type="warning" effect="light">
          共 {{ highValueList.length }} 件
        </el-tag>
      </div>
      <el-table :data="highValueList" stripe @row-click="goToDetail" style="cursor: pointer;">
        <el-table-column label="饰品" min-width="240">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div class="photo-box">
                <img v-if="row.photo" :src="'/uploads/' + row.photo" />
                <el-icon v-else color="#ccc"><Picture /></el-icon>
              </div>
              <div>
                <div style="font-weight: 600; color: #4a2c2a;">{{ row.name }}</div>
                <div style="font-size: 12px; color: #999; margin-top: 2px;">
                  <el-icon size="12" color="#c9a96e"><Location /></el-icon>
                  {{ row.storage_location || '未标记位置' }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="品类" width="120" prop="category" />
        <el-table-column label="当前估值" width="140" align="right">
          <template #default="{ row }">
            <span style="color: #c9a96e; font-weight: 700; font-size: 15px;">¥{{ formatNumber(row.current_valuation) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="建议保额" width="140" align="right">
          <template #default="{ row }">
            <span style="color: #4a2c2a; font-weight: 600;">¥{{ formatNumber(row.suggested_insurance) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="riskTagType(row.risk_level)" effect="light" size="small">
              <el-icon v-if="row.risk_level === 'high'"><WarningFilled /></el-icon>
              <el-icon v-else-if="row.risk_level === 'medium'"><InfoFilled /></el-icon>
              {{ riskLabel(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="佩戴频次" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="wearTagType(row.wear_frequency)" effect="plain" size="small">
              {{ wearLabel(row.wear_frequency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click.stop="openValuationDialog(row)">
              <el-icon><Plus /></el-icon>创建估值
            </el-button>
            <el-button size="small" type="success" link @click.stop="handleCalculate(row)">
              <el-icon><Edit /></el-icon>重新计算
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="valuationDialogVisible" :title="valuationDialogTitle" width="560px">
      <el-form :model="valuationForm" ref="valuationFormRef" :rules="valuationRules" label-width="100px">
        <el-form-item label="饰品">
          <span style="color: #4a2c2a; font-weight: 500;">{{ selectedAccessory?.name }}</span>
        </el-form-item>
        <el-form-item label="估值日期" prop="valuation_date">
          <el-date-picker v-model="valuationForm.valuation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="估值方法" prop="method">
          <el-select v-model="valuationForm.method" placeholder="选择估值方法" style="width: 100%;">
            <el-option label="市场比较法" value="market" />
            <el-option label="成本法" value="cost" />
            <el-option label="收益法" value="income" />
            <el-option label="专家评估" value="expert" />
          </el-select>
        </el-form-item>
        <el-form-item label="估值金额" prop="value">
          <el-input-number v-model="valuationForm.value" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="建议保额">
          <el-input-number v-model="valuationForm.suggested_insurance" :min="0" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="风险等级" prop="risk_level">
          <el-select v-model="valuationForm.risk_level" placeholder="选择风险等级" style="width: 100%;">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="valuationForm.notes" type="textarea" :rows="3" placeholder="填写估值备注说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="valuationDialogVisible = false">取消</el-button>
        <el-button class="btn-primary" @click="handleSubmitValuation">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Histogram, Coin, TrendCharts, PieChart, Goods,
  Plus, Edit, WarningFilled, InfoFilled, Picture, Location, Refresh
} from '@element-plus/icons-vue'
import {
  getValuationOverview, calculateValuation, createValuation,
  getAccessories, getMeta
} from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const overview = ref({})
const highValueList = ref([])
const trendChartRef = ref(null)
const categoryChartRef = ref(null)
const riskChartRef = ref(null)

const valuationDialogVisible = ref(false)
const valuationDialogTitle = ref('创建估值记录')
const selectedAccessory = ref(null)
const valuationFormRef = ref(null)

const defaultValuationForm = () => ({
  accessory_id: null,
  valuation_date: new Date().toISOString().split('T')[0],
  method: 'market',
  value: 0,
  suggested_insurance: 0,
  risk_level: 'low',
  notes: ''
})
const valuationForm = reactive(defaultValuationForm())

const valuationRules = {
  valuation_date: [{ required: true, message: '请选择估值日期', trigger: 'change' }],
  method: [{ required: true, message: '请选择估值方法', trigger: 'change' }],
  value: [{ required: true, message: '请输入估值金额', trigger: 'blur' }],
  risk_level: [{ required: true, message: '请选择风险等级', trigger: 'change' }]
}

const riskColorMap = {
  low: '#6ba878',
  medium: '#e8a45b',
  high: '#c83c3c'
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

const riskLabel = (level) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

const riskTagType = (level) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

const wearLabel = (freq) => {
  const map = { frequent: '频繁', occasional: '偶尔', rare: '很少', never: '从未' }
  return map[freq] || freq || '未知'
}

const wearTagType = (freq) => {
  const map = { frequent: 'success', occasional: 'warning', rare: 'info', never: 'danger' }
  return map[freq] || 'info'
}

const goToDetail = (row) => {
  router.push('/accessories')
}

const refreshData = async () => {
  await loadData()
  ElMessage.success('数据已刷新')
}

const openValuationDialog = (accessory) => {
  selectedAccessory.value = accessory
  Object.assign(valuationForm, defaultValuationForm())
  valuationForm.accessory_id = accessory.id
  valuationForm.value = accessory.current_valuation || 0
  valuationForm.suggested_insurance = accessory.suggested_insurance || 0
  valuationForm.risk_level = accessory.risk_level || 'low'
  valuationDialogVisible.value = true
}

const handleCalculate = async (accessory) => {
  try {
    const result = await calculateValuation(accessory.id)
    ElMessage.success('重新计算估值成功')
    Object.assign(accessory, result)
    await loadData()
  } catch (e) {
    ElMessage.error('计算估值失败')
  }
}

const handleSubmitValuation = async () => {
  await valuationFormRef.value.validate()
  try {
    const payload = {
      accessory_id: valuationForm.accessory_id,
      valuation_date: valuationForm.valuation_date,
      estimated_value: valuationForm.value,
      insurance_suggestion: valuationForm.suggested_insurance,
      risk_level: valuationForm.risk_level,
      condition_note: valuationForm.notes
    }
    await createValuation(payload)
    ElMessage.success('估值记录创建成功')
    valuationDialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

const loadData = async () => {
  const data = await getValuationOverview()
  overview.value = {
    total_valuation: data.total_asset_value || 0,
    total_purchase_price: data.total_purchase_value || 0,
    depreciation_rate: data.depreciation_rate || 0,
    accessory_count: data.accessory_count || 0,
    valuation_trend: (data.valuation_trend || []).map(d => ({
      date: d.date || d.month,
      total_value: d.total_value || d.value
    })),
    category_value_distribution: (data.category_distribution || []).map(d => ({
      category: d.category,
      total_value: d.total_value || d.value
    })),
    risk_value_distribution: (data.risk_distribution || []).map(d => ({
      risk_level: d.risk_level || d.level,
      risk_label: d.label || '',
      total_value: d.total_value || d.value
    })).filter(d => d.total_value > 0)
  }
  highValueList.value = (data.top_valuable || []).map(v => ({
    id: v.accessory?.id,
    photo: v.accessory?.photo,
    name: v.accessory?.name,
    category: v.accessory?.category,
    material: v.accessory?.material,
    storage_location: v.accessory?.storage_location,
    current_valuation: v.estimated_value,
    suggested_insurance: v.insurance_suggestion,
    risk_level: v.risk_level,
    wear_frequency: v.wear_frequency,
    depreciation_reason: v.depreciation_reason
  }))
  await nextTick()
  renderCharts()
}

const renderCharts = () => {
  if (trendChartRef.value && overview.value.valuation_trend?.length) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}<br/>估值: ¥{c}' },
      grid: { left: 60, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: overview.value.valuation_trend.map(d => d.month || d.date),
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'value',
        name: '¥',
        splitLine: { lineStyle: { color: '#f5f0e8' } },
        axisLabel: { color: '#999' }
      },
      series: [{
        type: 'line',
        smooth: true,
        data: overview.value.valuation_trend.map(d => d.total_value || d.value),
        lineStyle: { color: '#c9a96e', width: 3 },
        itemStyle: { color: '#c9a96e' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(201, 169, 110, 0.3)' },
            { offset: 1, color: 'rgba(201, 169, 110, 0.05)' }
          ])
        },
        symbol: 'circle',
        symbolSize: 6
      }]
    })
  }

  if (categoryChartRef.value && overview.value.category_value_distribution?.length) {
    const chart = echarts.init(categoryChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 10 },
        data: overview.value.category_value_distribution.map((d, i) => ({
          name: d.category,
          value: d.total_value,
          itemStyle: { color: categoryColors[i % categoryColors.length] }
        }))
      }]
    })
  }

  if (riskChartRef.value && overview.value.risk_value_distribution?.length) {
    const chart = echarts.init(riskChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 10 },
        data: overview.value.risk_value_distribution.map(d => ({
          name: riskLabel(d.risk_level),
          value: d.total_value,
          itemStyle: { color: riskColorMap[d.risk_level] || '#c9a96e' }
        }))
      }]
    })
  }
}

const categoryColors = [
  '#c9a96e', '#5a8cc8', '#6ba878', '#e8a45b', '#9b7ab8',
  '#e8b4a0', '#c86b3c', '#8b6f47', '#7aa8e0', '#8ac492'
]

onMounted(loadData)
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 12px rgba(74, 44, 42, 0.06);
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(74, 44, 42, 0.1);
}

.stat-ic {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-v {
  font-size: 24px;
  font-weight: 700;
  color: #4a2c2a;
  line-height: 1.2;
}

.stat-l {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.photo-box {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: #f5efe6;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.photo-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

:deep(.el-table__row:hover) {
  background-color: #faf7f5 !important;
}
</style>
