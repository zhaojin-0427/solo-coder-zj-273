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
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStatistics } from '@/api'

const stats = ref({})
const colorChartRef = ref(null)
const categoryChartRef = ref(null)

const colorMap = {
  '金色': '#d4a855', '银色': '#c0c0c0', '玫瑰金': '#e8b4a0', '白色': '#f8f5f0',
  '黑色': '#333333', '红色': '#c83c3c', '粉色': '#f0a0b0', '蓝色': '#5a8cc8',
  '绿色': '#6ba878', '紫色': '#9b7ab8', '米色': '#e8dcc8', '棕色': '#8b6f47',
  '灰色': '#999999', '黄色': '#e8c85a'
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
</style>
