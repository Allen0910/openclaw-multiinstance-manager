<template>
  <div class="metrics-page">
    <div class="metrics-toolbar">
      <h2 class="page-title">性能分析</h2>
      <div class="toolbar-actions">
        <el-select v-model="selectedInstance" placeholder="选择实例" size="small" style="width: 180px">
          <el-option v-for="instance in instances" :key="instance.id" :label="instance.name" :value="instance.id" />
        </el-select>
        <el-select v-model="timeRange" size="small" style="width: 120px">
          <el-option label="最近1小时" value="1h" />
          <el-option label="最近6小时" value="6h" />
          <el-option label="最近24小时" value="24h" />
          <el-option label="最近7天" value="7d" />
        </el-select>
        <el-button type="primary" size="small" class="btn-primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="stat-card card-glow">
        <div class="stat-icon cpu">
          <el-icon size="24"><Cpu /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-label">平均CPU使用率</p>
          <h3 class="stat-value cpu count-animation">{{ summary.avgCpu }}<span>%</span></h3>
          <div class="stat-trend" :class="summary.cpuTrend >= 0 ? 'trend-up' : 'trend-down'">
            <el-icon v-if="summary.cpuTrend >= 0"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
            <span>{{ Math.abs(summary.cpuTrend) }}%</span>
          </div>
        </div>
      </div>
      <div class="stat-card card-glow">
        <div class="stat-icon memory">
          <el-icon size="24"><Monitor /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-label">平均内存使用率</p>
          <h3 class="stat-value memory count-animation">{{ summary.avgMemory }}<span>%</span></h3>
          <div class="stat-trend" :class="summary.memoryTrend >= 0 ? 'trend-up' : 'trend-down'">
            <el-icon v-if="summary.memoryTrend >= 0"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
            <span>{{ Math.abs(summary.memoryTrend) }}%</span>
          </div>
        </div>
      </div>
      <div class="stat-card card-glow">
        <div class="stat-icon disk">
          <el-icon size="24"><HardDisk /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-label">平均磁盘使用率</p>
          <h3 class="stat-value disk count-animation">{{ summary.avgDisk }}<span>%</span></h3>
          <div class="stat-trend" :class="summary.diskTrend >= 0 ? 'trend-up' : 'trend-down'">
            <el-icon v-if="summary.diskTrend >= 0"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
            <span>{{ Math.abs(summary.diskTrend) }}%</span>
          </div>
        </div>
      </div>
      <div class="stat-card card-glow">
        <div class="stat-icon success">
          <el-icon size="24"><Odometer /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-label">任务执行成功率</p>
          <h3 class="stat-value success count-animation">{{ summary.successRate }}<span>%</span></h3>
          <div class="stat-trend" :class="summary.successTrend >= 0 ? 'trend-up' : 'trend-down'">
            <el-icon v-if="summary.successTrend >= 0"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
            <span>{{ Math.abs(summary.successTrend) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-container section-gap">
      <div class="chart-header">
        <h3>CPU 使用率趋势</h3>
      </div>
      <div ref="cpuChartRef" style="height: 300px"></div>
    </div>

    <el-row :gutter="20" class="section-gap">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="chart-container">
          <div class="chart-header">
            <h3>内存使用率趋势</h3>
          </div>
          <div ref="memoryChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="chart-container">
          <div class="chart-header">
            <h3>磁盘使用率趋势</h3>
          </div>
          <div ref="diskChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>

    <div class="chart-container">
      <div class="chart-header">
        <h3>网络流量趋势</h3>
      </div>
      <div ref="networkChartRef" style="height: 300px"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, onBeforeUnmount, computed } from 'vue'
import { Cpu, Monitor, Files as HardDisk, Refresh, Odometer, Top, Bottom } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskChartRef = ref(null)
const networkChartRef = ref(null)
const selectedInstance = ref(null)
const timeRange = ref('24h')
const chartInstances = []
let resizeHandler = null
let themeObserver = null

const instances = ref([])
const metrics = ref([])
const taskSuccessStats = ref({
  rate: 0,
  trend: 0
})

const RANGE_CONFIG = {
  '1h': { count: 12 },
  '6h': { count: 24 },
  '24h': { count: 48 },
  '7d': { count: 84 }
}

const getRangeConfig = () => RANGE_CONFIG[timeRange.value] || RANGE_CONFIG['24h']

const getThemeVar = (name, fallback) => {
  const scope = document.querySelector('.app-container') || document.documentElement
  const value = getComputedStyle(scope).getPropertyValue(name).trim()
  return value || fallback
}

const hexToRgba = (hex, alpha) => {
  const normalized = hex.replace('#', '')
  if (normalized.length !== 6) return `rgba(255, 255, 255, ${alpha})`
  const r = Number.parseInt(normalized.slice(0, 2), 16)
  const g = Number.parseInt(normalized.slice(2, 4), 16)
  const b = Number.parseInt(normalized.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const resolveChartPalette = () => {
  const bgPrimary = getThemeVar('--bg-primary', '#0e121b')
  const lightMode = bgPrimary.toLowerCase().startsWith('#f')
  const fallbackBorder = getThemeVar('--border-color', '#34435c')
  return {
    lightMode,
    text: getThemeVar('--text-primary', '#f4f7fd'),
    textSecondary: lightMode ? '#3d5881' : getThemeVar('--text-secondary', '#c8d1e3'),
    border: lightMode ? '#a8bdd9' : fallbackBorder,
    splitLine: lightMode ? 'rgba(145, 165, 194, 0.56)' : hexToRgba(fallbackBorder, 0.5),
    cpu: lightMode ? '#e65a2f' : getThemeVar('--primary-color', '#ff7a45'),
    memory: lightMode ? '#14996b' : getThemeVar('--success-color', '#20bf7a'),
    disk: lightMode ? '#cb8a24' : getThemeVar('--warning-color', '#f3a833'),
    networkIn: lightMode ? '#208db3' : getThemeVar('--accent-color', '#35d2c0'),
    networkOut: lightMode ? '#e25162' : getThemeVar('--danger-color', '#ff5f6d'),
    tooltipBg: lightMode ? 'rgba(255, 255, 255, 0.96)' : 'rgba(14, 18, 27, 0.96)',
    tooltipText: lightMode ? '#1e293f' : '#f4f7fd',
    lineWidth: lightMode ? 2.8 : 2.5,
    areaTopAlpha: lightMode ? 0.4 : 0.28,
    areaBottomAlpha: lightMode ? 0.08 : 0.03
  }
}

const toNumber = (value) => Number(Number(value || 0).toFixed(1))

const average = (arr) => {
  if (!arr.length) return 0
  return toNumber(arr.reduce((sum, cur) => sum + Number(cur || 0), 0) / arr.length)
}

const trendByHalf = (arr) => {
  if (arr.length < 4) return 0
  const half = Math.floor(arr.length / 2)
  const first = average(arr.slice(0, half))
  const second = average(arr.slice(half))
  return toNumber(second - first)
}

const selectedInstanceInfo = computed(() => {
  return instances.value.find(item => item.id === selectedInstance.value) || null
})

const summary = computed(() => {
  const source = metrics.value
  if (!source.length) {
    const fallback = selectedInstanceInfo.value
    return {
      avgCpu: toNumber(fallback?.cpu_usage || 0),
      avgMemory: toNumber(fallback?.memory_usage || 0),
      avgDisk: toNumber(fallback?.disk_usage || 0),
      cpuTrend: 0,
      memoryTrend: 0,
      diskTrend: 0,
      successRate: taskSuccessStats.value.rate,
      successTrend: taskSuccessStats.value.trend
    }
  }

  const cpu = source.map(item => item.cpu_usage)
  const memory = source.map(item => item.memory_usage)
  const disk = source.map(item => item.disk_usage)

  return {
    avgCpu: average(cpu),
    avgMemory: average(memory),
    avgDisk: average(disk),
    cpuTrend: trendByHalf(cpu),
    memoryTrend: trendByHalf(memory),
    diskTrend: trendByHalf(disk),
    successRate: taskSuccessStats.value.rate,
    successTrend: taskSuccessStats.value.trend
  }
})

const formatMetricLabel = (timestamp) => {
  const time = new Date(timestamp)
  if (Number.isNaN(time.getTime())) return '-'
  const hh = String(time.getHours()).padStart(2, '0')
  const mm = String(time.getMinutes()).padStart(2, '0')
  if (timeRange.value === '7d') {
    const month = String(time.getMonth() + 1).padStart(2, '0')
    const day = String(time.getDate()).padStart(2, '0')
    return `${month}-${day} ${hh}:${mm}`
  }
  return `${hh}:${mm}`
}

const createLineSeries = (name, color, data, colors) => ({
  name,
  type: 'line',
  smooth: 0.42,
  showSymbol: false,
  data,
  lineStyle: { color, width: colors.lineWidth },
  areaStyle: {
    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: hexToRgba(color, colors.areaTopAlpha) },
      { offset: 1, color: hexToRgba(color, colors.areaBottomAlpha) }
    ])
  }
})

const createBaseOption = (timeData, colors, yAxisFormatter = '{value}%') => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: colors.tooltipBg,
    borderColor: colors.border,
    borderWidth: 1,
    textStyle: {
      color: colors.tooltipText,
      fontSize: 12
    }
  },
  grid: {
    left: '2%',
    right: '3%',
    bottom: '2%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: timeData,
    axisLine: {
      lineStyle: { color: colors.border }
    },
    axisLabel: {
      color: colors.textSecondary,
      fontSize: 10,
      hideOverlap: true
    },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    min: 0,
    axisLine: { show: false },
    axisLabel: {
      color: colors.textSecondary,
      fontSize: 10,
      formatter: yAxisFormatter
    },
    splitLine: {
      lineStyle: {
        color: colors.splitLine,
        type: 'dashed'
      }
    }
  }
})

const disposeCharts = () => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  while (chartInstances.length > 0) {
    const chart = chartInstances.pop()
    if (!chart) continue
    const disposed = typeof chart.isDisposed === 'function' ? chart.isDisposed() : false
    if (!disposed) chart.dispose()
  }
}

const fetchInstances = async () => {
  try {
    const res = await api.get('/instances/', { params: { limit: 200 } })
    instances.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    instances.value = []
  }

  if (instances.value.length > 0) {
    if (!selectedInstance.value || !instances.value.some(item => item.id === selectedInstance.value)) {
      selectedInstance.value = instances.value[0].id
    }
  } else {
    selectedInstance.value = null
  }
}

const fetchMetrics = async () => {
  if (!selectedInstance.value) {
    metrics.value = []
    return
  }
  try {
    const res = await api.get(`/instances/${selectedInstance.value}/metrics/`, {
      params: { limit: getRangeConfig().count }
    })
    metrics.value = Array.isArray(res.data) ? res.data.slice().reverse() : []
  } catch (error) {
    metrics.value = []
  }
}

const fetchTaskSuccessStats = async () => {
  if (!selectedInstance.value) {
    taskSuccessStats.value = { rate: 0, trend: 0 }
    return
  }

  try {
    const res = await api.get('/tasks/', {
      params: { instance_id: selectedInstance.value, limit: 200 }
    })
    const list = Array.isArray(res.data) ? res.data : []
    const finished = list.filter(item => ['success', 'failed', 'canceled'].includes(item.status))
    const successCount = finished.filter(item => item.status === 'success').length
    const rate = finished.length ? toNumber((successCount / finished.length) * 100) : 0

    let trend = 0
    if (finished.length >= 6) {
      const half = Math.floor(finished.length / 2)
      const first = finished.slice(0, half)
      const second = finished.slice(half)
      const firstRate = first.length
        ? (first.filter(item => item.status === 'success').length / first.length) * 100
        : 0
      const secondRate = second.length
        ? (second.filter(item => item.status === 'success').length / second.length) * 100
        : 0
      trend = toNumber(secondRate - firstRate)
    }

    taskSuccessStats.value = { rate, trend }
  } catch (error) {
    taskSuccessStats.value = { rate: 0, trend: 0 }
  }
}

const buildSourcePoints = () => {
  if (metrics.value.length > 0) return metrics.value
  const fallback = selectedInstanceInfo.value
  if (!fallback) return []
  return [
    {
      created_at: new Date().toISOString(),
      cpu_usage: fallback.cpu_usage || 0,
      memory_usage: fallback.memory_usage || 0,
      disk_usage: fallback.disk_usage || 0,
      network_in: 0,
      network_out: 0
    }
  ]
}

const initCharts = () => {
  if (!cpuChartRef.value || !memoryChartRef.value || !diskChartRef.value || !networkChartRef.value) return

  const source = buildSourcePoints()
  if (!source.length) {
    disposeCharts()
    return
  }

  disposeCharts()
  const timeData = source.map(item => formatMetricLabel(item.created_at))
  const cpuData = source.map(item => toNumber(item.cpu_usage))
  const memoryData = source.map(item => toNumber(item.memory_usage))
  const diskData = source.map(item => toNumber(item.disk_usage))
  const networkInData = source.map(item => toNumber(item.network_in))
  const networkOutData = source.map(item => toNumber(item.network_out))
  const colors = resolveChartPalette()

  const baseOption = createBaseOption(timeData, colors)

  const cpuChart = echarts.init(cpuChartRef.value)
  cpuChart.setOption({
    ...baseOption,
    yAxis: {
      ...baseOption.yAxis,
      max: 100
    },
    series: [createLineSeries('CPU', colors.cpu, cpuData, colors)]
  })

  const memoryChart = echarts.init(memoryChartRef.value)
  memoryChart.setOption({
    ...baseOption,
    yAxis: {
      ...baseOption.yAxis,
      max: 100
    },
    series: [createLineSeries('内存', colors.memory, memoryData, colors)]
  })

  const diskChart = echarts.init(diskChartRef.value)
  diskChart.setOption({
    ...baseOption,
    yAxis: {
      ...baseOption.yAxis,
      max: 100
    },
    series: [createLineSeries('磁盘', colors.disk, diskData, colors)]
  })

  const networkChart = echarts.init(networkChartRef.value)
  networkChart.setOption({
    ...createBaseOption(
      timeData,
      colors,
      value => (value >= 1024 ? `${(value / 1024).toFixed(1)} MB/s` : `${Math.round(value)} KB/s`)
    ),
    legend: {
      data: ['入站流量', '出站流量'],
      textStyle: {
        color: colors.textSecondary,
        fontSize: 11
      },
      top: 8,
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 4
    },
    grid: {
      left: '2%',
      right: '3%',
      bottom: '2%',
      top: '16%',
      containLabel: true
    },
    series: [
      createLineSeries('入站流量', colors.networkIn, networkInData, colors),
      createLineSeries('出站流量', colors.networkOut, networkOutData, colors)
    ]
  })

  chartInstances.push(cpuChart, memoryChart, diskChart, networkChart)
  resizeHandler = () => chartInstances.forEach(chart => chart.resize())
  window.addEventListener('resize', resizeHandler)
}

const loadMetricsData = async () => {
  await Promise.all([fetchMetrics(), fetchTaskSuccessStats()])
  initCharts()
}

const refreshData = async () => {
  await loadMetricsData()
  ElMessage.success('图表已刷新')
}

watch([timeRange, selectedInstance], async () => {
  await loadMetricsData()
})

onMounted(async () => {
  await fetchInstances()
  await nextTick()
  await loadMetricsData()

  const appContainer = document.querySelector('.app-container')
  if (appContainer) {
    themeObserver = new MutationObserver(() => {
      initCharts()
    })
    themeObserver.observe(appContainer, {
      attributes: true,
      attributeFilter: ['class']
    })
  }
})

onBeforeUnmount(() => {
  disposeCharts()
  if (themeObserver) {
    themeObserver.disconnect()
    themeObserver = null
  }
})
</script>

<style scoped>
.metrics-page {
  width: 100%;
}

.metrics-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.section-gap {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.stat-icon.cpu {
  background: linear-gradient(135deg, color-mix(in srgb, var(--primary-color) 18%, transparent), color-mix(in srgb, var(--primary-color) 8%, transparent));
  color: var(--primary-color);
}

.stat-icon.memory {
  background: linear-gradient(135deg, color-mix(in srgb, var(--success-color) 18%, transparent), color-mix(in srgb, var(--success-color) 8%, transparent));
  color: var(--success-color);
}

.stat-icon.disk {
  background: linear-gradient(135deg, color-mix(in srgb, var(--warning-color) 18%, transparent), color-mix(in srgb, var(--warning-color) 8%, transparent));
  color: var(--warning-color);
}

.stat-icon.success {
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent-color) 18%, transparent), color-mix(in srgb, var(--accent-color) 8%, transparent));
  color: var(--accent-color);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-value span {
  font-size: 0.62em;
  margin-left: 2px;
}

.stat-value.cpu {
  color: var(--primary-color);
}

.stat-value.memory {
  color: var(--success-color);
}

.stat-value.disk {
  color: var(--warning-color);
}

.stat-value.success {
  color: var(--accent-color);
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.trend-up {
  color: var(--success-color);
}

.trend-down {
  color: var(--danger-color);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.chart-header h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

@media (max-width: 900px) {
  .toolbar-actions {
    width: 100%;
  }
}
</style>
