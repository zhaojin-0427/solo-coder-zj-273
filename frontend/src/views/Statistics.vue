<template>
  <div class="page-container">
    <div class="page-title">
      <el-icon><DataAnalysis /></el-icon>
      数据统计
    </div>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #c9a96e, #e8c87a);">
          <el-icon :size="22" color="#fff"><Collection /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.total || 0 }}</div>
          <div class="stat-l">饰品总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
          <el-icon :size="22" color="#fff"><Histogram /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.total_wears || 0 }}</div>
          <div class="stat-l">累计佩戴次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #6ba878, #8ac492);">
          <el-icon :size="22" color="#fff"><SuccessFilled /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.active_rate || 0 }}%</div>
          <div class="stat-l">30日活跃率 ({{ stats.active_count || 0 }}件)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #e8b4a0, #f0c8b8);">
          <el-icon :size="22" color="#fff"><DataLine /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.utilization_rate || 0 }}%</div>
          <div class="stat-l">整体利用率</div>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">色系分布</div>
          <div ref="colorChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">品类分布</div>
          <div ref="categoryChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <div class="section-title" style="margin-top: 10px; margin-bottom: 16px; padding-left: 10px; border-left: 3px solid #c9a96e; font-size: 16px; font-weight: 600; color: #4a2c2a;">
      旅行/活动行程数据
    </div>

    <div class="stat-cards">
      <div class="stat-card" @click="goToTrips" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #c9a96e, #e8c87a);">
          <el-icon :size="22" color="#fff"><Suitcase /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.trip_count || 0 }}</div>
          <div class="stat-l">行程总数</div>
        </div>
      </div>
      <div class="stat-card" @click="goToTrips" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #6ba878, #8ac492);">
          <el-icon :size="22" color="#fff"><Box /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.trip_packing_rate || 0 }}%</div>
          <div class="stat-l">整体打包完成率 ({{ stats.trip_packed_items || 0 }}/{{ stats.trip_total_items || 0 }})</div>
        </div>
      </div>
      <div class="stat-card" @click="goToTrips" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
          <el-icon :size="22" color="#fff"><RefreshRight /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.trip_plan_utilization || 0 }}%</div>
          <div class="stat-l">计划内饰品利用率 ({{ stats.trip_unique_count || 0 }}件)</div>
        </div>
      </div>
      <div class="stat-card" @click="goToTrips" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #9b7ab8, #b598d0);">
          <el-icon :size="22" color="#fff"><Calendar /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.upcoming_trips?.length || 0 }}</div>
          <div class="stat-l">即将到来的行程</div>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">
            行程打包进度
            <el-tag v-if="stats.trip_packing_stats?.length" size="small" type="info" effect="light" style="margin-left: 10px;">
              {{ stats.trip_packing_stats.length }} 个行程
            </el-tag>
          </div>
          <div v-if="!stats.trip_packing_stats?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><Suitcase /></el-icon>
            <p>还没有行程数据，去行李规划创建行程吧</p>
          </div>
          <div v-else class="trip-packing-list">
            <div v-for="t in stats.trip_packing_stats" :key="t.trip_id" class="trip-packing-item">
              <div class="tpi-header" @click="goToTrip(t.trip_id)">
                <div class="tpi-name">{{ t.trip_name }}</div>
                <el-tag :type="t.status === 'completed' ? 'success' : t.status === 'packing' ? 'warning' : 'info'" size="small">
                  {{ { planning: '规划中', packing: '打包中', completed: '已完成' }[t.status] || t.status }}
                </el-tag>
              </div>
              <div class="tpi-meta">
                <el-icon color="#c9a96e" size="12"><Location /></el-icon>
                {{ t.destination || '未指定' }}
                <span class="sep">·</span>
                {{ t.start_date }} ~ {{ t.end_date }}
              </div>
              <div class="tpi-progress">
                <el-progress
                  :percentage="t.packing_rate"
                  :color="t.packing_rate >= 100 ? '#6ba878' : t.packing_rate >= 50 ? '#c9a96e' : '#e8a45b'"
                  :stroke-width="8"
                />
                <span class="tpi-count">{{ t.packed_items }}/{{ t.total_items }} 件 · {{ t.unique_count }} 件单品</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">
            旅行高频色系
            <el-tag size="small" type="warning" effect="light" style="margin-left: 10px;">历史行程偏好</el-tag>
          </div>
          <div v-if="!stats.trip_color_distribution?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><Brush /></el-icon>
            <p>还没有行程色系数据</p>
          </div>
          <div ref="tripColorChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <div v-if="stats.upcoming_trips?.length > 0" class="card">
      <div class="section-title">
        即将到来的行程
        <el-tag type="warning" effect="light" style="margin-left: 10px;">请提前准备打包</el-tag>
      </div>
      <div class="upcoming-list">
        <div v-for="trip in stats.upcoming_trips" :key="trip.id" class="upcoming-card" @click="goToTrip(trip.id)">
          <div class="uc-date-box">
            <div class="uc-month">{{ formatMonth(trip.start_date) }}</div>
            <div class="uc-day">{{ formatDay(trip.start_date) }}</div>
          </div>
          <div class="uc-info">
            <div class="uc-name">{{ trip.name }}</div>
            <div class="uc-meta">
              <el-icon color="#c9a96e"><Location /></el-icon>
              {{ trip.destination || '未指定目的地' }}
              <span class="sep">·</span>
              {{ trip.start_date }} ~ {{ trip.end_date }}
            </div>
          </div>
          <el-button class="btn-primary" size="small">
            查看清单
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="stats.unpacked_reminders?.length > 0" class="card">
      <div class="section-title">
        未打包提醒
        <el-tag type="danger" effect="light" style="margin-left: 10px;">
          还有 {{ stats.unpacked_reminders.length }} 件饰品待打包
        </el-tag>
      </div>
      <el-table :data="stats.unpacked_reminders.slice(0, 20)" stripe size="small">
        <el-table-column label="行程" width="160">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToTrip(row.trip_id)">
              {{ row.trip_name }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="日期" width="100">
          <template #default="{ row }">
            第{{ row.day_index }}天
            <div style="font-size: 11px; color: #999;">{{ row.date }}</div>
          </template>
        </el-table-column>
        <el-table-column label="饰品" min-width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="width: 36px; height: 36px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                <img v-if="row.accessory.photo" :src="'/uploads/' + row.accessory.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                <el-icon v-else color="#ccc"><Picture /></el-icon>
              </div>
              <div>
                <div style="font-weight: 500; font-size: 13px;">
                  {{ row.accessory.name }}
                  <el-tag v-if="row.is_spare" size="small" type="warning" effect="light" style="margin-left: 6px;">备用</el-tag>
                </div>
                <div style="font-size: 11px; color: #999;">
                  <span class="color-dot" :style="{ background: colorMap[row.accessory.color_family] }"></span>
                  {{ row.accessory.category }} · {{ row.accessory.color_family }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="收纳位置" width="140" prop="accessory.storage_location">
          <template #default="{ row }">
            {{ row.accessory.storage_location || '未标记' }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="card">
      <div class="section-title">高频搭配组合</div>
      <div v-if="stats.frequent_combos && stats.frequent_combos.length > 0" class="freq-list">
        <div v-for="(f, i) in stats.frequent_combos" :key="f.id" class="freq-item">
          <span class="freq-rank" :class="i < 3 ? 'top' : ''">{{ i + 1 }}</span>
          <div class="freq-info">
            <div class="freq-name">
              {{ f.name }}
              <el-tag v-if="f.occasion" size="small" type="success" style="margin-left: 8px;">{{ f.occasion }}</el-tag>
            </div>
            <div class="freq-pieces">
              <span v-if="f.necklace">项链: {{ f.necklace.name }}</span>
              <span v-if="f.earring">耳环: {{ f.earring.name }}</span>
              <span v-if="f.bracelet">手链: {{ f.bracelet.name }}</span>
            </div>
          </div>
          <div class="freq-count">
            <el-icon color="#c9a96e"><Histogram /></el-icon>
            {{ f.use_count }} 次
          </div>
        </div>
      </div>
      <div v-else class="empty-tip" style="padding: 30px;">
        <el-icon><Star /></el-icon>
        <p>还没有常用搭配，使用收藏的搭配记录次数吧</p>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        长期未佩戴提醒
        <el-tag type="danger" effect="light" style="margin-left: 10px;">超过 30 天</el-tag>
      </div>
      <div v-if="stats.long_unworn && stats.long_unworn.length > 0">
        <el-table :data="stats.long_unworn" stripe>
          <el-table-column label="饰品" min-width="200">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                  <img v-if="row.photo" :src="'/uploads/' + row.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                  <el-icon v-else color="#ccc"><Picture /></el-icon>
                </div>
                <div>
                  <div style="font-weight: 500;">{{ row.name }}</div>
                  <div style="font-size: 12px; color: #999;">{{ row.category }} · {{ row.material }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="色系" width="100">
            <template #default="{ row }">
              <span class="color-dot" :style="{ background: colorMap[row.color_family] }"></span>
              {{ row.color_family }}
            </template>
          </el-table-column>
          <el-table-column label="收纳位置" prop="storage_location" width="140" />
          <el-table-column label="上次佩戴" prop="last_worn_date" width="120">
            <template #default="{ row }">
              {{ row.last_worn_date || '从未佩戴' }}
            </template>
          </el-table-column>
          <el-table-column label="未佩戴天数" width="120">
            <template #default="{ row }">
              <el-tag type="danger" effect="light">{{ row.days_unworn }} 天</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="empty-tip" style="padding: 30px;">
        <el-icon><SuccessFilled /></el-icon>
        <p>太棒了！所有饰品在 30 天内都有佩戴记录</p>
      </div>
    </div>

    <div class="section-title" style="margin-top: 10px; margin-bottom: 16px; padding-left: 10px; border-left: 3px solid #9b7ab8; font-size: 16px; font-weight: 600; color: #4a2c2a;">
      借出与保养维修统计
    </div>

    <div class="stat-cards">
      <div class="stat-card" @click="goToTracking" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #5a8cc8, #7aa8e0);">
          <el-icon :size="22" color="#fff"><User /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.active_loan_count || 0 }}</div>
          <div class="stat-l">当前借出</div>
        </div>
      </div>
      <div class="stat-card" @click="goToTracking" style="cursor: pointer;">
        <div class="stat-ic" style="background: linear-gradient(135deg, #c83c3c, #e87878);">
          <el-icon :size="22" color="#fff"><Warning /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ stats.overdue_loan_count || 0 }}</div>
          <div class="stat-l">逾期未还</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #e8a45b, #f0c088);">
          <el-icon :size="22" color="#fff"><Setting /></el-icon>
        </div>
        <div>
          <div class="stat-v">{{ (stats.active_maintenance_count || 0) + (stats.active_repair_count || 0) }}</div>
          <div class="stat-l">保养/维修中 (保养{{ stats.active_maintenance_count || 0 }}·维修{{ stats.active_repair_count || 0 }})</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-ic" style="background: linear-gradient(135deg, #9b7ab8, #b598d0);">
          <el-icon :size="22" color="#fff"><Money /></el-icon>
        </div>
        <div>
          <div class="stat-v">¥{{ stats.total_maintenance_cost || 0 }}</div>
          <div class="stat-l">累计维修保养费用</div>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">
            饰品状态分布
          </div>
          <div ref="statusChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="card">
          <div class="section-title">
            维修保养费用趋势
          </div>
          <div v-if="!stats.cost_trend?.length" class="empty-tip" style="padding: 30px;">
            <el-icon><Money /></el-icon>
            <p>暂无费用数据</p>
          </div>
          <div v-else ref="costTrendChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <div v-if="stats.high_risk_accessories?.length > 0" class="card">
      <div class="section-title">
        高风险频繁维修饰品
        <el-tag type="danger" effect="light" style="margin-left: 10px;">
          {{ stats.high_risk_accessories.length }} 件维修 ≥ 2 次
        </el-tag>
      </div>
      <el-table :data="stats.high_risk_accessories" stripe>
        <el-table-column label="饰品" min-width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                <img v-if="row.photo" :src="'/uploads/' + row.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                <el-icon v-else color="#ccc"><Picture /></el-icon>
              </div>
              <div>
                <div style="font-weight: 500;">{{ row.name }}</div>
                <div style="font-size: 12px; color: #999;">{{ row.category }} · {{ row.material }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="维修次数" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="danger" effect="light">{{ row.repair_count }} 次</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="累计费用" width="140" align="center">
          <template #default="{ row }">
            <span style="color: #c83c3c; font-weight: 600;">¥{{ row.total_repair_cost }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="stats.maintenance_reminders_30d?.length > 0" class="card">
      <div class="section-title">
        未来 30 天保养提醒
        <el-tag type="warning" effect="light" style="margin-left: 10px;">
          {{ stats.maintenance_reminders_30d.length }} 件需保养
        </el-tag>
      </div>
      <el-table :data="stats.maintenance_reminders_30d" stripe>
        <el-table-column label="饰品" min-width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="width: 40px; height: 40px; border-radius: 6px; background: #f5efe6; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                <img v-if="row.photo" :src="'/uploads/' + row.photo" style="width: 100%; height: 100%; object-fit: cover;" />
                <el-icon v-else color="#ccc"><Picture /></el-icon>
              </div>
              <div>
                <div style="font-weight: 500;">{{ row.name }}</div>
                <div style="font-size: 12px; color: #999;">{{ row.category }} · {{ row.material }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="下次保养日期" width="160">
          <template #default="{ row }">
            <el-tag :type="row.days_until <= 7 ? 'danger' : row.days_until <= 14 ? 'warning' : 'success'" effect="light">
              {{ row.next_maintenance_date }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="倒计时" width="120" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.days_until <= 7 ? '#c83c3c' : row.days_until <= 14 ? '#e8a45b' : '#6ba878', fontWeight: 600 }">
              还剩 {{ row.days_until }} 天
            </span>
          </template>
        </el-table-column>
        <el-table-column label="保养周期" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.maintenance_cycle_days > 0">每 {{ row.maintenance_cycle_days }} 天</span>
            <span v-else style="color: #999;">未设置</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { Suitcase, Box, RefreshRight, Calendar, Location, Brush, Picture, DataAnalysis, Collection, Histogram, SuccessFilled, DataLine, Star, User, Warning, Setting, Money } from '@element-plus/icons-vue'
import { getStatistics } from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const stats = ref({})
const colorChartRef = ref(null)
const categoryChartRef = ref(null)
const tripColorChartRef = ref(null)
const statusChartRef = ref(null)
const costTrendChartRef = ref(null)

const statusColorMap = {
  in_stock: '#6ba878',
  lent: '#5a8cc8',
  overdue: '#c83c3c',
  maintenance: '#e8a45b',
  repair: '#c86b3c'
}

const statusLabelMap = {
  in_stock: '在库',
  lent: '已借出',
  overdue: '逾期未还',
  maintenance: '保养中',
  repair: '维修中'
}

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
}

const goToTrips = () => {
  router.push('/trips')
}

const goToTracking = () => {
  router.push('/tracking')
}

const goToTrip = (id) => {
  router.push('/trips')
  setTimeout(() => {
    window.dispatchEvent(new CustomEvent('view-trip', { detail: { id } }))
  }, 100)
}

const formatMonth = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月`
}

const formatDay = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.getDate()
}

const loadData = async () => {
  stats.value = await getStatistics()
  await nextTick()
  renderCharts()
}

const renderCharts = () => {
  if (colorChartRef.value && stats.value.color_distribution) {
    const chart = echarts.init(colorChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}件 ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
        data: stats.value.color_distribution.map(d => ({
          name: d.color,
          value: d.count,
          itemStyle: { color: colorMap[d.color] || '#c9a96e' }
        }))
      }]
    })
  }

  if (categoryChartRef.value && stats.value.category_distribution) {
    const chart = echarts.init(categoryChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: 40, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: stats.value.category_distribution.map(d => d.category),
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f5f0e8' } },
        axisLabel: { color: '#999' }
      },
      series: [{
        type: 'bar',
        data: stats.value.category_distribution.map(d => ({
          value: d.count,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#e8c87a' },
              { offset: 1, color: '#c9a96e' }
            ]),
            borderRadius: [6, 6, 0, 0]
          }
        })),
        barWidth: '40%',
        label: { show: true, position: 'top', color: '#4a2c2a', fontWeight: 600 }
      }]
    })
  }

  if (tripColorChartRef.value && stats.value.trip_color_distribution?.length) {
    const chart = echarts.init(tripColorChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}次 ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        roseType: 'radius',
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
        data: stats.value.trip_color_distribution.map(d => ({
          name: d.color,
          value: d.count,
          itemStyle: { color: colorMap[d.color] || '#c9a96e' }
        }))
      }]
    })
  }

  if (statusChartRef.value && stats.value.status_distribution?.length) {
    const chart = echarts.init(statusChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}件 ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
        data: stats.value.status_distribution.map(d => ({
          name: statusLabelMap[d.status] || d.status,
          value: d.count,
          itemStyle: { color: statusColorMap[d.status] || '#c9a96e' }
        }))
      }]
    })
  }

  if (costTrendChartRef.value && stats.value.cost_trend?.length) {
    const chart = echarts.init(costTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: ¥{c}' },
      grid: { left: 50, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: stats.value.cost_trend.map(d => d.month),
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
        type: 'bar',
        data: stats.value.cost_trend.map(d => ({
          value: d.total_cost,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#b598d0' },
              { offset: 1, color: '#9b7ab8' }
            ]),
            borderRadius: [6, 6, 0, 0]
          }
        })),
        barWidth: '40%',
        label: { show: true, position: 'top', color: '#4a2c2a', fontWeight: 600, formatter: '¥{c}' }
      }]
    })
  }
}

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

.freq-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.freq-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: #faf7f5;
  border-radius: 10px;
}

.freq-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e8ddcc;
  color: #8b6f47;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.freq-rank.top {
  background: linear-gradient(135deg, #c9a96e, #e8c87a);
  color: #fff;
}

.freq-info {
  flex: 1;
  min-width: 0;
}

.freq-name {
  font-size: 14px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 4px;
}

.freq-pieces {
  font-size: 12px;
  color: #888;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.freq-count {
  font-size: 13px;
  color: #8b6f47;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.trip-packing-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.trip-packing-item {
  padding: 12px 14px;
  background: #faf7f5;
  border-radius: 10px;
}

.tpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  cursor: pointer;
}

.tpi-name {
  font-size: 14px;
  font-weight: 600;
  color: #4a2c2a;
}

.tpi-meta {
  font-size: 12px;
  color: #888;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tpi-meta .sep {
  color: #ccc;
  margin: 0 4px;
}

.tpi-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tpi-progress .el-progress {
  flex: 1;
}

.tpi-count {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
}

.upcoming-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.upcoming-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg, #fff9ef 0%, #faf7f5 100%);
  border-radius: 12px;
  border: 1px solid #f0e8dd;
  cursor: pointer;
  transition: all 0.2s;
}

.upcoming-card:hover {
  box-shadow: 0 4px 16px rgba(74, 44, 42, 0.08);
  transform: translateY(-2px);
}

.uc-date-box {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #c9a96e, #e8c87a);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.uc-month {
  font-size: 11px;
  opacity: 0.9;
}

.uc-day {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.uc-info {
  flex: 1;
  min-width: 0;
}

.uc-name {
  font-size: 15px;
  font-weight: 600;
  color: #4a2c2a;
  margin-bottom: 4px;
}

.uc-meta {
  font-size: 12px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 4px;
}

.uc-meta .sep {
  color: #ccc;
  margin: 0 4px;
}
</style>
