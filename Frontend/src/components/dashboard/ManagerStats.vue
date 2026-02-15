<template>
  <div class="stats-container">
    <div class="stats-header">
      <h2 class="section-title">Executive Dashboard</h2>
      <div class="controls">
        <el-select v-model="timeRange" placeholder="Period" style="width: 140px">
          <el-option label="Last 30 Days" value="30" />
          <el-option label="Last Quarter" value="90" />
          <el-option label="Year to Date" value="365" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchStats">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="stats-tabs" type="border-card">

      <el-tab-pane label="Overview" name="overview">
        <div class="tab-content-grid">
          <div class="chart-card full-width">
            <div class="card-header"><h3>Revenue Trend</h3></div>
            <div ref="trendChartRef" class="chart-body"></div>
          </div>
          <div class="chart-card">
            <div class="card-header"><h3>Top Selling Products</h3></div>
            <div ref="productChartRef" class="chart-body"></div>
          </div>
           <div class="chart-card">
            <div class="card-header"><h3>Sales by Category</h3></div>
            <div ref="categoryChartRef" class="chart-body"></div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Customer Intelligence" name="customers">
        <div class="tab-content-grid">
          <div class="chart-card full-width">
            <div class="card-header">
              <h3>The "Whale" Hunt: B2B vs B2C Value</h3>
              <span class="subtitle">Comparison of Average Order Value vs Total Volume</span>
            </div>
            <div ref="whaleChartRef" class="chart-body"></div>
          </div>

          <div class="chart-card">
            <div class="card-header"><h3>Consumer Demographics</h3></div>
            <div ref="ageChartRef" class="chart-body"></div>
          </div>
           <div class="chart-card">
            <div class="card-header"><h3>Business Sectors</h3></div>
            <div ref="bizChartRef" class="chart-body"></div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Operations & Team" name="operations">
        <div class="tab-content-grid">
          <div class="chart-card full-width">
            <div class="card-header">
              <h3>Sales Team Efficiency (ROI)</h3>
              <span class="subtitle">Revenue generated per dollar of salary paid</span>
            </div>
            <el-table :data="statsData.salesEfficiency" style="width: 100%">
              <el-table-column prop="salesperson_name" label="Salesperson" />
              <el-table-column prop="store_location" label="Location" />
              <el-table-column prop="revenue_generated" label="Revenue" sortable>
                <template #default="scope">${{ scope.row.revenue_generated?.toLocaleString() }}</template>
              </el-table-column>
              <el-table-column prop="salary_multiplier" label="ROI Multiplier" sortable align="center">
                <template #default="scope">
                  <el-tag :type="getRoiColor(scope.row.salary_multiplier)">
                    {{ scope.row.salary_multiplier }}x
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="chart-card full-width">
            <div class="card-header">
              <h3>Regional Power Rankings</h3>
            </div>
            <el-table :data="statsData.regionalRankings" style="width: 100%" stripe>
              <el-table-column prop="region_name" label="Region" width="150" />
              <el-table-column prop="manager_name" label="Manager" width="180" />
              <el-table-column prop="store_count" label="Stores" width="100" align="center" />
              <el-table-column prop="total_revenue" label="Total Revenue" sortable>
                <template #default="scope">
                  <b>${{ scope.row.total_revenue?.toLocaleString() }}</b>
                </template>
              </el-table-column>
            </el-table>
          </div>


        </div>
      </el-tab-pane>

      <el-tab-pane label="Inventory Health" name="inventory">
        <div class="tab-content-grid">
          <div class="chart-card full-width border-danger">
            <div class="card-header">
              <h3 class="text-danger">The "Dead Stock" Report</h3>
              <span class="subtitle">High inventory items (>20 units) with low recent sales (&lt;5 units)</span>
            </div>
            <el-table
              :data="statsData.deadStock"
              style="width: 100%"
              :default-sort="{ prop: 'current_stock', order: 'descending' }"
            >
              <el-table-column prop="product_name" label="Product" />
              <el-table-column prop="store_name" label="Store Location" width="200" />

              <el-table-column
                prop="current_stock"
                label="Stock Level"
                width="120"
                align="center"
                sortable
                :sort-method="sortByCurrentStock"
              >
                <template #default="scope">
                  <span style="color: #f56c6c; font-weight: bold;">{{ scope.row.current_stock }}</span>
                </template>
              </el-table-column>

              <el-table-column
                prop="units_sold"
                label="Recent Sales"
                width="120"
                align="center"
                sortable
                :sort-method="sortByUnitsSold"
              />

              <el-table-column
                prop="revenue_generated"
                label="Revenue"
                width="150"
                sortable
                :sort-method="sortByRevenue"
              >
                <template #default="scope">
                  ${{ Number(scope.row.revenue_generated).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </template>
              </el-table-column>

              <el-table-column label="Action" width="120" v-if="false">
                <template #default>
                  <el-button size="small" type="warning" plain>Discount</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getManagerStats } from '../../api/stats'
import { Refresh } from '@element-plus/icons-vue'

// --- State ---
const activeTab = ref('overview') // Default to overview
const loading = ref(false)
const timeRange = ref('30')

// --- Data ---
const statsData = ref({
  whaleData: [],
  regionalRankings: [],
  deadStock: [],
  salesEfficiency: [],
  trend: { dates: [], values: [] },
  topProducts: { names: [], values: [] },
  categories: []
})

// --- Chart Refs ---
const trendChartRef = ref(null)
const productChartRef = ref(null)
const categoryChartRef = ref(null)
const whaleChartRef = ref(null)
const ageChartRef = ref(null)
const bizChartRef = ref(null)

// --- Chart Instances ---
let trendChart = null
let productChart = null
let categoryChart = null
let whaleChart = null
let ageChart = null
let bizChart = null

// --- Helpers ---
const getRoiColor = (multiplier) => {
  if (multiplier > 5) return 'success'
  if (multiplier > 2) return 'warning'
  return 'danger'
}

const sortByCurrentStock = (a, b) => Number(a.current_stock) - Number(b.current_stock)
const sortByUnitsSold = (a, b) => Number(a.units_sold) - Number(b.units_sold)
const sortByRevenue = (a, b) => Number(a.revenue_generated) - Number(b.revenue_generated)


const pieTooltipFormatter = {
  trigger: 'item',
  formatter: (params) => `<b>${params.name}</b><br/>$${params.value.toLocaleString()} (${params.percent}%)`
}

const fetchStats = async () => {
  loading.value = true
  try {
    const { data } = await getManagerStats({ range: timeRange.value })
    statsData.value = data
    nextTick(() => updateCharts(data))
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const updateCharts = (data) => {
  // 1. Overview Charts
  if (trendChartRef.value) {
    if (!trendChart) trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => `$${params[0].value}` },
      xAxis: { type: 'category', data: data.trend?.dates || [] },
      yAxis: { type: 'value' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      series: [{ data: data.trend?.values || [], type: 'line', smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#409eff' } }]
    })
  }

  if (productChartRef.value) {
    if (!productChart) productChart = echarts.init(productChartRef.value)
    productChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: data.topProducts?.names || [], axisLabel: { width: 100, overflow: 'truncate' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      series: [{ type: 'bar', data: data.topProducts?.values || [], itemStyle: { color: '#67c23a' } }]
    })
  }

  if (categoryChartRef.value) {
    if (!categoryChart) categoryChart = echarts.init(categoryChartRef.value)
    categoryChart.setOption({
      tooltip: pieTooltipFormatter,
      legend: { type: 'scroll', bottom: 0 },
      series: [{ type: 'pie', radius: '60%', center: ['50%', '45%'], data: data.categories || [] }]
    })
  }

  // 2. Customer Charts (Whale, Age, Biz)
  if (whaleChartRef.value && data.whaleData) {
    if (!whaleChart) whaleChart = echarts.init(whaleChartRef.value)
    const categories = data.whaleData.map(d => d.customer_type)
    const avgOrder = data.whaleData.map(d => d.avg_order_value)
    const totalRev = data.whaleData.map(d => d.total_revenue)

    whaleChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['Avg Order Value', 'Total Revenue'] },
      xAxis: { type: 'category', data: categories },
      yAxis: [
        { type: 'value', name: 'Avg Order Value', axisLabel: { formatter: '${value}' } },
        { type: 'value', name: 'Total Revenue', axisLabel: { formatter: '${value}' } }
      ],
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      series: [
        { name: 'Avg Order Value', type: 'bar', data: avgOrder, itemStyle: { color: '#fac858' } },
        { name: 'Total Revenue', type: 'line', yAxisIndex: 1, data: totalRev, smooth: true, itemStyle: { color: '#5470c6' } }
      ]
    })
  }

  if (ageChartRef.value) {
    if (!ageChart) ageChart = echarts.init(ageChartRef.value)
    ageChart.setOption({
      tooltip: pieTooltipFormatter,
      color: ['#ee6666', '#fac858', '#91cc75', '#5470c6'],
      legend: { bottom: 0 },
      series: [{
        name: 'Age Group',
        type: 'pie',
        radius: '60%',
        center: ['50%', '45%'],
        data: data.demographics || [],
        roseType: 'radius',
        itemStyle: { borderRadius: 5 }
      }]
    })
  }

  if (bizChartRef.value) {
    if (!bizChart) bizChart = echarts.init(bizChartRef.value)
    bizChart.setOption({
      tooltip: pieTooltipFormatter,
      legend: { type: 'scroll', bottom: 0 },
      series: [{
        name: 'Industry',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data: data.bizCategories || []
      }]
    })
  }
}

watch(activeTab, () => {
  nextTick(() => {
    [trendChart, productChart, categoryChart, whaleChart, ageChart, bizChart].forEach(c => c?.resize())
  })
})

const handleResize = () => {
  [trendChart, productChart, categoryChart, whaleChart, ageChart, bizChart].forEach(c => c?.resize())
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  [trendChart, productChart, categoryChart, whaleChart, ageChart, bizChart].forEach(c => c?.dispose())
})
</script>

<style scoped>
.stats-container { padding: 1rem; max-width: 100%; overflow-x: hidden; }
.stats-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.section-title { font-size: 20px; font-weight: 600; color: #303133; margin: 0; }
.controls { display: flex; gap: 10px; }
.charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 1.5rem; width: 100%; }
.tab-content-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 1.5rem; width: 100%; }
.full-width { grid-column: 1 / -1; }
.chart-card { background: #fff; border-radius: 8px; border: 1px solid #e4e7ed; padding: 1.5rem; min-height: 350px; height: auto; display: flex; flex-direction: column; }
.card-header h3 { margin: 0 0 0.5rem 0; font-size: 16px; color: #606266; }
.subtitle { font-size: 12px; color: #909399; display: block; margin-bottom: 1rem; }
.chart-body { flex: 1; width: 100%; min-height: 300px; }
.border-danger { border-left: 4px solid #f56c6c; }
.text-danger { color: #f56c6c; }

/* Responsive */
@media (max-width: 1024px) {
  .charts-grid, .tab-content-grid { grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); }
}
@media (max-width: 768px) {
  .tab-content-grid { grid-template-columns: 1fr; }
  .stats-header { flex-direction: column; align-items: flex-start; }
}
</style>