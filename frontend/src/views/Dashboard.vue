<template>
  <div class="dashboard">
    <!-- 命令行终端和快捷操作 - 并排布局 -->
    <div class="terminal-layout">
      <!-- 命令行终端 -->
      <div class="terminal-container card-glow">
        <div class="terminal-header">
          <div class="terminal-title">
            <el-icon><Console /></el-icon>
            <span>命令行终端</span>
          </div>
          <div class="terminal-actions">
            <el-select v-model="selectedInstance" placeholder="选择实例" size="small" style="width: 160px; margin-right: 10px">
              <el-option label="全部实例" value="all" />
              <el-option v-for="instance in instances" :key="instance.id" :label="instance.name" :value="instance.id" />
            </el-select>
            <el-button size="small" :icon="Delete" circle @click="clearTerminal" title="清空终端" />
          </div>
        </div>
        <div class="terminal-output" ref="terminalOutput">
          <div v-for="(line, index) in terminalLines" :key="index" :class="['terminal-line', line.type]">
            <span class="line-prompt" v-if="line.type === 'input'">$ </span>
            <span class="line-content" v-html="line.content"></span>
          </div>
        </div>
        <div class="terminal-input-area">
          <span class="input-prompt">$</span>
          <input
            v-model="currentCommand"
            @keyup.enter="executeCommand"
            class="terminal-input"
            placeholder="输入命令并按回车执行..."
            :disabled="terminalExecuting"
          />
        </div>
      </div>

      <!-- 快捷操作面板 -->
      <div class="quick-panel card-glow">
        <div class="quick-panel-header">
          <div class="terminal-title">
            <el-icon><Operation /></el-icon>
            <span>快捷操作</span>
          </div>
          <!-- 飞书操作下拉菜单 -->
          <el-dropdown trigger="click" @command="runQuickCommand">
            <el-button size="small" type="primary" class="feishu-dropdown-btn">
              <el-icon><Promotion /></el-icon>
              飞书操作
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="/feishu auth">飞书授权</el-dropdown-item>
                <el-dropdown-item command="/feishu start">飞书启动</el-dropdown-item>
                <el-dropdown-item command="/feishu doctor">飞书体检</el-dropdown-item>
                <el-dropdown-item command="feishu-plugin-onboard install" divided>插件安装</el-dropdown-item>
                <el-dropdown-item command="feishu-plugin-onboard doctor">插件体检</el-dropdown-item>
                <el-dropdown-item command="feishu-plugin-onboard doctor --fix">自动修复</el-dropdown-item>
                <el-dropdown-item command="openclaw plugins list" divided>插件列表</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="quick-panel-content">
          <!-- 网关控制 -->
          <div class="quick-section">
            <div class="quick-section-title">网关控制</div>
            <div class="quick-btns">
              <el-button size="small" @click="runQuickCommand('openclaw gateway install')">安装</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw gateway start')">启动</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw gateway status')">状态</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw gateway restart')">重启</el-button>
            </div>
          </div>
          <!-- 配置与诊断 -->
          <div class="quick-section">
            <div class="quick-section-title">配置与诊断</div>
            <div class="quick-btns">
              <el-button size="small" @click="runQuickCommand('openclaw version')">版本</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw health')">状态</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw doctor')">诊断</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw help')">帮助</el-button>
            </div>
          </div>
          <!-- 流式配置 -->
          <div class="quick-section">
            <div class="quick-section-title">流式配置</div>
            <div class="quick-btns">
              <el-button size="small" type="success" @click="runQuickCommand('openclaw config set channels.feishu.streaming true')">开启</el-button>
              <el-button size="small" type="warning" @click="runQuickCommand('openclaw config set channels.feishu.streaming false')">关闭</el-button>
              <el-button size="small" @click="runQuickCommand('openclaw config get channels.feishu')">查看</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 顶部统计卡片 -->
    <div class="dashboard-grid">
      <div class="stat-card card-glow" v-for="card in statCards" :key="card.key">
        <div class="stat-icon" :style="{ background: card.bg }">
          <component :is="card.icon" size="24" />
        </div>
        <div class="stat-content">
          <p class="stat-label">{{ card.label }}</p>
          <h3 class="stat-value count-animation" :style="{ color: card.color }">
            {{ card.value }}<span v-if="card.suffix">{{ card.suffix }}</span>
          </h3>
          <div class="stat-trend" :class="card.trend > 0 ? 'trend-up' : 'trend-down'">
            <el-icon v-if="card.trend > 0"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
            <span>{{ Math.abs(card.trend) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <div class="chart-container">
          <div class="chart-header">
            <h3>资源使用率趋势</h3>
            <el-select v-model="timeRange" size="small" style="width: 120px">
              <el-option label="今日" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
            </el-select>
          </div>
          <div ref="chartRef" class="chart-content" style="height: 350px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" :lg="8">
        <div class="chart-container">
          <div class="chart-header">
            <h3>资源分布</h3>
          </div>
          <div ref="pieChartRef" class="chart-content" style="height: 350px"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 实例状态 -->
    <div class="card-glow">
      <div class="card-header">
        <h3>实例实时状态</h3>
        <div class="card-actions">
          <el-button type="primary" size="small" class="btn-primary" @click="refreshInstances">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      <div class="table-custom">
        <el-table :data="instances" border stripe>
          <el-table-column prop="name" label="实例名称" width="150">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <span class="status-dot" :class="scope.row.status === 'online' ? 'status-online' : 'status-offline'"></span>
                <span style="margin-left: 8px">{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="host" label="主机地址" width="150" />
          <el-table-column prop="version" label="版本" width="120" />
          <el-table-column prop="cpu_usage" label="CPU使用率">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <div class="progress-custom" style="flex: 1; margin-right: 10px">
                  <div 
                    class="progress-custom-bar" 
                    :class="getProgressClass(scope.row.cpu_usage)"
                    :style="{ width: `${Math.round(scope.row.cpu_usage)}%` }"
                  ></div>
                </div>
                <span style="min-width: 50px; text-align: right">{{ scope.row.cpu_usage.toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="memory_usage" label="内存使用率">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <div class="progress-custom" style="flex: 1; margin-right: 10px">
                  <div 
                    class="progress-custom-bar" 
                    :class="getProgressClass(scope.row.memory_usage)"
                    :style="{ width: `${Math.round(scope.row.memory_usage)}%` }"
                  ></div>
                </div>
                <span style="min-width: 50px; text-align: right">{{ scope.row.memory_usage.toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="disk_usage" label="磁盘使用率">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <div class="progress-custom" style="flex: 1; margin-right: 10px">
                  <div 
                    class="progress-custom-bar" 
                    :class="getProgressClass(scope.row.disk_usage)"
                    :style="{ width: `${Math.round(scope.row.disk_usage)}%` }"
                  ></div>
                </div>
                <span style="min-width: 50px; text-align: right">{{ scope.row.disk_usage.toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="last_heartbeat" label="最后心跳" width="180" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'online' ? 'success' : 'danger'" class="tag-success" size="small">
                {{ scope.row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button size="small" type="primary" class="btn-primary" link @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 最近告警 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="card-glow">
          <div class="card-header">
            <h3>最近告警</h3>
            <el-button type="text" style="color: var(--primary-color)" @click="$router.push('/alerts')">查看全部</el-button>
          </div>
          <div class="alert-list">
            <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
              <div class="alert-icon" :class="`alert-${alert.level}`">
                <el-icon v-if="alert.level === 'warning'"><Warning /></el-icon>
                <el-icon v-else-if="alert.level === 'error'"><CircleClose /></el-icon>
                <el-icon v-else><InfoFilled /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-desc">{{ alert.content }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="card-glow">
          <div class="card-header">
            <h3>正在运行的任务</h3>
            <el-button type="text" style="color: var(--primary-color)" @click="$router.push('/tasks')">查看全部</el-button>
          </div>
          <div class="task-list">
            <div class="task-item" v-for="task in runningTasks" :key="task.id">
              <div class="task-info">
                <div class="task-name">{{ task.name }}</div>
                <div class="task-meta">实例: {{ task.instance }} | 开始时间: {{ task.start_time }}</div>
              </div>
              <div class="task-progress">
                <el-progress :percentage="task.progress" :show-text="false" color="var(--primary-color)" />
                <span>{{ task.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="instanceDetailVisible" title="实例详情" width="820px" class="dialog-custom">
      <div v-loading="detailLoading">
        <el-descriptions v-if="detailInstance" :column="2" border>
          <el-descriptions-item label="实例名称">{{ detailInstance.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detailInstance.status }}</el-descriptions-item>
          <el-descriptions-item label="主机地址">{{ detailInstance.host }}:{{ detailInstance.port }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ detailInstance.version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="CPU">{{ Number(detailInstance.cpu_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="内存">{{ Number(detailInstance.memory_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="磁盘">{{ Number(detailInstance.disk_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="最后心跳">{{ detailInstance.last_heartbeat || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>最近任务</h4>
          <el-table :data="detailTasks" border stripe style="width: 100%">
            <el-table-column prop="name" label="任务名称" min-width="180" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="created_at" label="创建时间" min-width="180" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { Cpu, Monitor, Files as HardDisk, Warning, InfoFilled, CircleClose, Refresh, Top, Bottom, Delete, Monitor as Console, Operation, ArrowDown, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '../utils/axios'

const activeTerminalTab = ref('terminal')
const chartRef = ref(null)
const pieChartRef = ref(null)
const terminalOutput = ref(null)
const timeRange = ref('today')
const instances = ref([])
const recentAlerts = ref([])
const runningTasks = ref([])
const dashboardMetrics = ref([])
const terminalExecuting = ref(false)
const instanceDetailVisible = ref(false)
const detailLoading = ref(false)
const detailInstance = ref(null)
const detailTasks = ref([])
let lineChartInstance = null
let pieChartInstance = null
let resizeHandler = null
let themeObserver = null
let refreshTimer = null

// 终端相关变量
const selectedInstance = ref('all')
const currentCommand = ref('')
const terminalLines = ref([
  { type: 'output', content: '欢迎使用 OpenClaw Manager 命令行终端' },
  { type: 'output', content: '选择目标实例后，输入命令并按回车执行' },
  { type: 'output', content: '----------------------------------------' }
])
const quickCommandGroups = [
  {
    title: '飞书授权',
    items: [
      { label: '飞书授权', command: '/feishu auth' },
      { label: '飞书启动', command: '/feishu start' },
      { label: '飞书体检', command: '/feishu doctor' }
    ]
  },
  {
    title: '网关控制',
    items: [
      { label: '安装网关', command: 'openclaw gateway install' },
      { label: '启动网关', command: 'openclaw gateway start' },
      { label: '网关状态', command: 'openclaw gateway status' },
      { label: '重启网关', command: 'openclaw gateway restart' }
    ]
  },
  {
    title: '飞书插件',
    items: [
      { label: '插件安装', command: 'feishu-plugin-onboard install' },
      { label: '插件体检', command: 'feishu-plugin-onboard doctor' },
      { label: '自动修复', command: 'feishu-plugin-onboard doctor --fix' },
      { label: '插件列表', command: 'openclaw plugins list' }
    ]
  },
  {
    title: '配置与诊断',
    items: [
      { label: '开启流式', command: 'openclaw config set channels.feishu.streaming true' },
      { label: '关闭流式', command: 'openclaw config set channels.feishu.streaming false' },
      { label: '飞书配置', command: 'openclaw config get channels.feishu' },
      { label: '版本信息', command: 'openclaw version' },
      { label: '运行状态', command: 'openclaw health' },
      { label: '系统诊断', command: 'openclaw doctor' },
      { label: '帮助命令', command: 'openclaw help' },
      { label: '未读告警', command: 'openclaw alerts list --unread' }
    ]
  }
]

const scrollTerminalToBottom = () => {
  nextTick(() => {
    if (terminalOutput.value) {
      terminalOutput.value.scrollTop = terminalOutput.value.scrollHeight
    }
  })
}

const escapeHtml = (input) => {
  return String(input)
    .replace(/&/g, '&')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#039;')
}

const formatTerminalOutput = (text) => {
  if (!text) return '(无输出)'
  return escapeHtml(text).replace(/\n/g, '<br/>')
}

const executeCommand = async () => {
  if (!currentCommand.value.trim() || terminalExecuting.value) return

  const cmd = currentCommand.value.trim()
  terminalLines.value.push({ type: 'input', content: escapeHtml(cmd) })

  if (['clear', 'openclaw clear'].includes(cmd.toLowerCase())) {
    clearTerminal()
    currentCommand.value = ''
    return
  }

  const payload = { command: cmd, timeout: 20 }
  if (selectedInstance.value !== 'all') {
    payload.instance_id = selectedInstance.value
  }

  terminalExecuting.value = true
  currentCommand.value = ''
  terminalLines.value.push({ type: 'output', content: '命令执行中...' })
  scrollTerminalToBottom()

  try {
    const res = await api.post('/terminal/execute', payload)
    const isError = Number(res.data?.exit_code || 0) !== 0
    terminalLines.value.push({
      type: isError ? 'error' : 'output',
      content: formatTerminalOutput(res.data?.output || res.data?.stdout || res.data?.stderr)
    })
  } catch (error) {
    terminalLines.value.push({
      type: 'error',
      content: formatTerminalOutput(error?.response?.data?.detail || '命令执行失败')
    })
  } finally {
    terminalExecuting.value = false
    scrollTerminalToBottom()
  }
}

const runQuickCommand = (command) => {
  currentCommand.value = command
  executeCommand()
}

const clearTerminal = () => {
  terminalLines.value = [
    { type: 'output', content: '终端已清空' },
    { type: 'output', content: '----------------------------------------' }
  ]
  scrollTerminalToBottom()
}

const statCards = ref([
  {
    key: 'instances',
    label: '在线实例',
    value: 2,
    suffix: '台',
    icon: Cpu,
    color: '#FF6B6B',
    bg: 'linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 71, 87, 0.1) 100%)',
    trend: 12.5
  },
  {
    key: 'tasks',
    label: '运行中任务',
    value: 3,
    suffix: '个',
    icon: Monitor,
    color: '#00B42A',
    bg: 'linear-gradient(135deg, rgba(0, 180, 42, 0.1) 0%, rgba(39, 195, 70, 0.1) 100%)',
    trend: -5.2
  },
  {
    key: 'alerts',
    label: '未读告警',
    value: 2,
    suffix: '条',
    icon: Warning,
    color: '#FF7D00',
    bg: 'linear-gradient(135deg, rgba(255, 125, 0, 0.1) 0%, rgba(255, 154, 46, 0.1) 100%)',
    trend: 25.8
  },
  {
    key: 'skills',
    label: '已安装技能',
    value: 16,
    suffix: '个',
    icon: HardDisk,
    color: '#722ED1',
    bg: 'linear-gradient(135deg, rgba(114, 46, 209, 0.1) 0%, rgba(146, 91, 255, 0.1) 100%)',
    trend: 8.3
  }
])

const updateStatCards = async () => {
  try {
    const [alertsRes, tasksRes, skillsRes] = await Promise.all([
      api.get('/alerts/', { params: { status: 'unread', limit: 200 } }),
      api.get('/tasks/', { params: { status: 'running', limit: 200 } }),
      api.get('/skills/', { params: { limit: 200 } })
    ])
    statCards.value[0].value = instances.value.filter(instance => instance.status === 'online').length
    statCards.value[1].value = tasksRes.data.length
    statCards.value[2].value = alertsRes.data.length
    statCards.value[3].value = skillsRes.data.length
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return '未知'
  const time = new Date(timestamp)
  if (Number.isNaN(time.getTime())) return String(timestamp)

  const diffMs = Date.now() - time.getTime()
  const diffMinutes = Math.floor(diffMs / 60000)
  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}小时前`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}天前`
}

const getProgressClass = (percentage) => {
  if (percentage < 70) return 'progress-success'
  if (percentage < 90) return 'progress-warning'
  return 'progress-danger'
}

const fetchInstances = async () => {
  try {
    const res = await api.get('/instances/', {
      params: { limit: 200 }
    })
    instances.value = res.data
    if (selectedInstance.value !== 'all') {
      const exists = instances.value.some(item => item.id === selectedInstance.value)
      if (!exists) {
        selectedInstance.value = 'all'
      }
    }
  } catch (error) {
    ElMessage.error('获取实例数据失败')
  }
}

const fetchAlerts = async () => {
  try {
    const res = await api.get('/alerts/', {
      params: { limit: 3 }
    })
    recentAlerts.value = res.data.map(alert => ({
      ...alert,
      time: formatRelativeTime(alert.created_at)
    }))
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks/', {
      params: { status: 'running', limit: 5 }
    })
    const instanceMap = new Map(instances.value.map(instance => [instance.id, instance.name]))
    runningTasks.value = res.data.map(task => ({
      id: task.id,
      name: task.name,
      instance: instanceMap.get(task.instance_id) || `实例#${task.instance_id}`,
      progress: task.status === 'running' ? 50 : 100,
      start_time: task.started_at || task.created_at || '-'
    }))
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const resolveChartTargetInstance = () => {
  if (selectedInstance.value !== 'all') {
    return instances.value.find(item => item.id === selectedInstance.value) || null
  }
  return instances.value.find(item => item.status === 'online') || instances.value[0] || null
}

const resolveChartMetricLimit = () => {
  const map = {
    today: 48,
    week: 84,
    month: 120
  }
  return map[timeRange.value] || 48
}

const formatMetricLabel = (timestamp) => {
  const time = new Date(timestamp)
  if (Number.isNaN(time.getTime())) return '-'
  const hh = String(time.getHours()).padStart(2, '0')
  const mm = String(time.getMinutes()).padStart(2, '0')
  if (timeRange.value === 'month') {
    const month = String(time.getMonth() + 1).padStart(2, '0')
    const day = String(time.getDate()).padStart(2, '0')
    return `${month}-${day} ${hh}:${mm}`
  }
  return `${hh}:${mm}`
}

const fetchDashboardMetrics = async () => {
  const target = resolveChartTargetInstance()
  if (!target) {
    dashboardMetrics.value = []
    return
  }

  try {
    const res = await api.get(`/instances/${target.id}/metrics/`, {
      params: { limit: resolveChartMetricLimit() }
    })
    const list = Array.isArray(res.data) ? res.data.slice().reverse() : []
    dashboardMetrics.value = list
  } catch (error) {
    dashboardMetrics.value = []
  }
}

const getThemeVar = (name, fallback) => {
  const scope = document.querySelector('.app-container') || document.documentElement
  const value = getComputedStyle(scope).getPropertyValue(name).trim()
  return value || fallback
}

const hexToRgba = (hex, alpha) => {
  const h = hex.replace('#', '')
  if (h.length !== 6) return `rgba(255, 255, 255, ${alpha})`
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const disposeCharts = () => {
  if (lineChartInstance) {
    lineChartInstance.dispose()
    lineChartInstance = null
  }
  if (pieChartInstance) {
    pieChartInstance.dispose()
    pieChartInstance = null
  }
}

const initCharts = () => {
  if (!chartRef.value || !pieChartRef.value) return
  disposeCharts()

  const bgPrimary = getThemeVar('--bg-primary', '#0e121b')
  const lightMode = bgPrimary.toLowerCase().startsWith('#f')
  const colors = {
    text: getThemeVar('--text-primary', '#f4f7fd'),
    textSecondary: lightMode ? '#3e587f' : getThemeVar('--text-secondary', '#c8d1e3'),
    border: getThemeVar('--border-color', '#34435c'),
    cpu: lightMode ? '#ea5a2a' : getThemeVar('--primary-color', '#ff7a45'),
    memory: lightMode ? '#0fa091' : getThemeVar('--accent-color', '#35d2c0'),
    disk: lightMode ? '#cf8b25' : getThemeVar('--warning-color', '#f3a833'),
    network: lightMode ? '#2a81b5' : getThemeVar('--info-color', '#7a8ead'),
    splitLine: lightMode ? 'rgba(145, 165, 192, 0.55)' : hexToRgba(getThemeVar('--border-color', '#34435c'), 0.45)
  }

  const tooltipBg = lightMode ? 'rgba(255, 255, 255, 0.98)' : 'rgba(14, 18, 27, 0.98)'
  const tooltipText = lightMode ? '#1e293f' : '#f4f7fd'
  const areaTopAlpha = lightMode ? 0.44 : 0.32
  const areaBottomAlpha = lightMode ? 0.07 : 0.03
  const hasMetrics = dashboardMetrics.value.length > 0
  const labels = hasMetrics
    ? dashboardMetrics.value.map(item => formatMetricLabel(item.created_at))
    : ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '现在']
  const cpuSeries = hasMetrics
    ? dashboardMetrics.value.map(item => Number(Number(item.cpu_usage || 0).toFixed(1)))
    : [32, 45, 38, 52, 68, 45, 42]
  const memorySeries = hasMetrics
    ? dashboardMetrics.value.map(item => Number(Number(item.memory_usage || 0).toFixed(1)))
    : [45, 52, 68, 58, 72, 65, 68]
  const diskSeries = hasMetrics
    ? dashboardMetrics.value.map(item => Number(Number(item.disk_usage || 0).toFixed(1)))
    : [62, 65, 68, 70, 72, 74, 75]
  const latestPoint = hasMetrics ? dashboardMetrics.value[dashboardMetrics.value.length - 1] : null

  lineChartInstance = echarts.init(chartRef.value)
  const lineOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: colors.border,
      borderWidth: 1,
      textStyle: {
        color: tooltipText,
        fontSize: 12
      }
    },
    legend: {
      data: ['CPU', '内存', '磁盘'],
      textStyle: {
        color: colors.textSecondary,
        fontSize: 12
      },
      top: 6,
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 4
    },
    grid: {
      left: '2%',
      right: '3%',
      bottom: '2%',
      top: '14%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels,
      axisLine: {
        lineStyle: { color: colors.border }
      },
      axisLabel: {
        color: colors.textSecondary,
        fontSize: 11
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      axisLabel: {
        color: colors.textSecondary,
        fontSize: 11,
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          color: colors.splitLine,
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        data: cpuSeries,
        lineStyle: { color: colors.cpu, width: 2.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: hexToRgba(colors.cpu, areaTopAlpha) },
            { offset: 1, color: hexToRgba(colors.cpu, areaBottomAlpha) }
          ])
        }
      },
      {
        name: '内存',
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        data: memorySeries,
        lineStyle: { color: colors.memory, width: 2.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: hexToRgba(colors.memory, lightMode ? 0.4 : 0.28) },
            { offset: 1, color: hexToRgba(colors.memory, lightMode ? 0.06 : 0.02) }
          ])
        }
      },
      {
        name: '磁盘',
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        data: diskSeries,
        lineStyle: { color: colors.disk, width: 2.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: hexToRgba(colors.disk, lightMode ? 0.38 : 0.26) },
            { offset: 1, color: hexToRgba(colors.disk, lightMode ? 0.06 : 0.02) }
          ])
        }
      }
    ]
  }
  lineChartInstance.setOption(lineOption)

  pieChartInstance = echarts.init(pieChartRef.value)
  const pieOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: tooltipBg,
      borderColor: colors.border,
      borderWidth: 1,
      textStyle: { color: tooltipText, fontSize: 12 },
      formatter: '{b}: {c}% ({d}%)'
    },
    series: [
      {
        name: '资源使用',
        type: 'pie',
        radius: ['58%', '82%'],
        center: ['50%', '52%'],
        itemStyle: {
          borderRadius: 8,
          borderColor: getThemeVar('--bg-card', '#1d2534'),
          borderWidth: 3
        },
        label: {
          show: true,
          color: lightMode ? '#2a4367' : colors.text,
          fontSize: 11,
          formatter: '{b}\\n{c}%'
        },
        labelLine: {
          lineStyle: { color: colors.border }
        },
        data: [
          { value: Number(Number(latestPoint?.cpu_usage || 42).toFixed(1)), name: 'CPU', itemStyle: { color: colors.cpu } },
          { value: Number(Number(latestPoint?.memory_usage || 68).toFixed(1)), name: '内存', itemStyle: { color: colors.memory } },
          { value: Number(Number(latestPoint?.disk_usage || 75).toFixed(1)), name: '磁盘', itemStyle: { color: colors.disk } },
          { value: 25, name: '网络', itemStyle: { color: colors.network } }
        ]
      }
    ]
  }
  pieChartInstance.setOption(pieOption)

  if (!resizeHandler) {
    resizeHandler = () => {
      if (lineChartInstance) lineChartInstance.resize()
      if (pieChartInstance) pieChartInstance.resize()
    }
    window.addEventListener('resize', resizeHandler)
  }
}

const refreshInstances = async () => {
  await fetchInstances()
  await Promise.all([fetchAlerts(), fetchTasks(), updateStatCards(), fetchDashboardMetrics()])
  initCharts()
  ElMessage.success('刷新成功')
}

const viewDetail = async (row) => {
  instanceDetailVisible.value = true
  detailLoading.value = true
  try {
    const [instanceRes, tasksRes] = await Promise.all([
      api.get(`/instances/${row.id}`),
      api.get(`/instances/${row.id}/tasks/`, { params: { limit: 10 } })
    ])
    detailInstance.value = instanceRes.data
    detailTasks.value = tasksRes.data
  } catch (error) {
    detailInstance.value = null
    detailTasks.value = []
  } finally {
    detailLoading.value = false
  }
}

onMounted(async () => {
  await nextTick()
  await fetchInstances()
  await Promise.all([fetchAlerts(), fetchTasks(), updateStatCards(), fetchDashboardMetrics()])
  initCharts()

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

  // 定时刷新数据
  refreshTimer = setInterval(() => {
    Promise.all([fetchInstances(), fetchAlerts(), fetchTasks(), updateStatCards(), fetchDashboardMetrics()]).then(() => {
      initCharts()
    })
  }, 30000)
})

watch([timeRange, selectedInstance], async () => {
  await fetchDashboardMetrics()
  initCharts()
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  if (themeObserver) {
    themeObserver.disconnect()
    themeObserver = null
  }
  disposeCharts()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

/* 终端和快捷操作并排布局 */
.terminal-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 16px;
  margin-bottom: var(--spacing-lg);
}

.terminal-container {
  margin-bottom: 0;
  padding: 0;
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-secondary) 95%, transparent), color-mix(in srgb, var(--bg-card) 88%, transparent));
  border-bottom: 1px solid var(--border-color);
}

.terminal-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
}

.terminal-title .el-icon {
  color: #00e5cc;
  font-size: 18px;
}

.terminal-actions {
  display: flex;
  align-items: center;
}

.terminal-output {
  height: 180px;
  overflow-y: auto;
  padding: var(--spacing-md);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-primary) 94%, transparent), color-mix(in srgb, var(--bg-secondary) 88%, transparent));
  border-top: 1px solid color-mix(in srgb, var(--border-color) 40%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--border-color) 40%, transparent);
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.terminal-line {
  margin-bottom: 4px;
  word-break: break-all;
}

.terminal-line.input {
  color: var(--accent-color);
}

.terminal-line.output {
  color: var(--text-secondary);
}

.terminal-line.error {
  color: var(--danger-color);
}

.line-prompt {
  color: var(--accent-color);
  font-weight: bold;
}

.line-content {
  color: inherit;
}

.terminal-input-area {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-secondary) 95%, transparent), color-mix(in srgb, var(--bg-card) 90%, transparent));
  border-top: 1px solid var(--border-color);
}

.input-prompt {
  color: var(--accent-color);
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  font-weight: bold;
  margin-right: var(--spacing-sm);
}

.terminal-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
}

.terminal-input::placeholder {
  color: var(--text-muted);
}

/* 快捷操作面板 */
.quick-panel {
  padding: 0;
  overflow: hidden;
}

.quick-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-secondary) 95%, transparent), color-mix(in srgb, var(--bg-card) 88%, transparent));
  border-bottom: 1px solid var(--border-color);
}

.feishu-dropdown-btn {
  background: var(--gradient-primary);
  border: none;
}

.quick-panel-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 280px;
  overflow-y: auto;
}

.quick-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px 12px;
}

.quick-section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quick-btns .el-button {
  font-size: 12px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-lg) 0;
  margin-bottom: var(--spacing-md);
}

.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.alert-list {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid color-mix(in srgb, var(--border-color) 75%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--bg-elevated) 92%, transparent);
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.alert-item:hover {
  border-color: color-mix(in srgb, var(--accent-color) 35%, var(--border-color));
  box-shadow: 0 8px 20px color-mix(in srgb, var(--bg-primary) 75%, transparent);
  transform: translateY(-1px);
}

.alert-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-warning {
  background: color-mix(in srgb, var(--warning-color) 16%, transparent);
  color: var(--warning-color);
}

.alert-error {
  background: color-mix(in srgb, var(--danger-color) 16%, transparent);
  color: var(--danger-color);
}

.alert-info {
  background: color-mix(in srgb, var(--accent-color) 16%, transparent);
  color: var(--accent-color);
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.alert-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  line-height: 1.5;
}

.alert-time {
  font-size: 12px;
  color: var(--text-muted);
}

.task-list {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid color-mix(in srgb, var(--border-color) 75%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--bg-elevated) 92%, transparent);
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.task-item:hover {
  border-color: color-mix(in srgb, var(--primary-color) 30%, var(--border-color));
  box-shadow: 0 8px 20px color-mix(in srgb, var(--bg-primary) 75%, transparent);
  transform: translateY(-1px);
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.task-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.task-progress {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 160px;
}

.task-progress :deep(.el-progress-bar__outer) {
  background: color-mix(in srgb, var(--border-color) 82%, transparent);
  border-radius: var(--radius-sm);
}

.task-progress span {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 38px;
  text-align: right;
  font-weight: 500;
}

.detail-section {
  margin-top: 14px;
}

.detail-section h4 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 14px;
}

@media (max-width: 1200px) {
  .terminal-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .quick-btns {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
