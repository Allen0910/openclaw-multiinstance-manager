<template>
  <div class="logs-page">
    <h2 class="page-title">日志查看</h2>
    
    <!-- 日志控制栏 -->
    <div class="card-glow" style="margin-bottom: 20px">
      <div class="log-controls">
        <div class="control-left">
          <el-select v-model="logSource" placeholder="日志来源" style="width: 150px" @change="loadLogs">
            <el-option label="全部日志" value="all" />
            <el-option label="系统日志" value="system" />
            <el-option label="访问日志" value="access" />
            <el-option label="错误日志" value="error" />
            <el-option label="调试日志" value="debug" />
          </el-select>
          
          <el-select v-model="logLevel" placeholder="日志级别" style="width: 120px" @change="loadLogs">
            <el-option label="全部级别" value="" />
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
          
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 360px"
            @change="loadLogs"
          />
        </div>
        
        <div class="control-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索日志内容"
            style="width: 200px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-button @click="loadLogs" :loading="loading">
            <el-icon><RefreshRight /></el-icon>
            刷新
          </el-button>
          
          <el-button type="primary" @click="exportLogs" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>
      
      <div class="auto-refresh">
        <el-switch v-model="autoRefresh" @change="toggleAutoRefresh" />
        <span class="switch-label">自动刷新 ({{ refreshInterval }}s)</span>
        <el-slider v-model="refreshInterval" :min="3" :max="30" :step="1" style="width: 100px; margin-left: 10px" :disabled="!autoRefresh" />
      </div>
    </div>

    <!-- 日志统计 -->
    <div class="log-stats" v-if="logStats">
      <div class="stat-item">
        <span class="stat-label">总日志数</span>
        <span class="stat-value">{{ logStats.total }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">DEBUG</span>
        <span class="stat-value debug">{{ logStats.debug }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">INFO</span>
        <span class="stat-value info">{{ logStats.info }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">WARNING</span>
        <span class="stat-value warning">{{ logStats.warning }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">ERROR</span>
        <span class="stat-value error">{{ logStats.error }}</span>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="card-glow">
      <div class="log-list" ref="logListRef">
        <div 
          v-for="(log, index) in filteredLogs" 
          :key="index" 
          :class="['log-item', log.level.toLowerCase()]"
        >
          <div class="log-time">{{ log.timestamp }}</div>
          <div class="log-level">{{ log.level }}</div>
          <div class="log-source">{{ log.source }}</div>
          <div class="log-message">{{ log.message }}</div>
        </div>
        
        <div v-if="filteredLogs.length === 0 && !loading" class="empty-logs">
          <el-icon :size="48"><Document /></el-icon>
          <p>暂无日志记录</p>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="totalLogs > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="totalLogs"
        layout="prev, pager, next, total"
        @current-change="loadLogs"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

const logSource = ref('all')
const logLevel = ref('')
const dateRange = ref([])
const searchKeyword = ref('')
const loading = ref(false)
const exporting = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref(5)
const currentPage = ref(1)
const pageSize = ref(50)
const totalLogs = ref(0)
const logStats = ref(null)
const logs = ref([])
const logListRef = ref(null)

let refreshTimer = null

// 模拟日志数据
const generateMockLogs = () => {
  const levels = ['DEBUG', 'INFO', 'INFO', 'INFO', 'WARNING', 'ERROR']
  const sources = ['system', 'api', 'database', 'auth', 'scheduler']
  const messages = [
    'Service started successfully',
    'User logged in from 192.168.1.100',
    'API request: GET /api/instances',
    'Database connection established',
    'Task completed: sync_instances',
    'Warning: High memory usage detected',
    'Error: Failed to connect to external service',
    'Cache cleared',
    'Configuration reloaded',
    'Background job started'
  ]
  
  const mockLogs = []
  const now = new Date()
  
  for (let i = 0; i < 50; i++) {
    const level = levels[Math.floor(Math.random() * levels.length)]
    const source = sources[Math.floor(Math.random() * sources.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    const time = new Date(now - i * 60000 * Math.random() * 10)
    
    mockLogs.push({
      timestamp: time.toISOString().replace('T', ' ').substring(0, 19),
      level,
      source,
      message
    })
  }
  
  return mockLogs
}

const filteredLogs = computed(() => {
  let result = logs.value
  
  if (logSource.value !== 'all') {
    result = result.filter(log => log.source === logSource.value)
  }
  
  if (logLevel.value) {
    result = result.filter(log => log.level === logLevel.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(log => 
      log.message.toLowerCase().includes(keyword) ||
      log.source.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const loadLogs = async () => {
  loading.value = true
  
  try {
    // 模拟日志数据
    logs.value = generateMockLogs()
    totalLogs.value = logs.value.length
    
    // 计算统计
    logStats.value = {
      total: logs.value.length,
      debug: logs.value.filter(l => l.level === 'DEBUG').length,
      info: logs.value.filter(l => l.level === 'INFO').length,
      warning: logs.value.filter(l => l.level === 'WARNING').length,
      error: logs.value.filter(l => l.level === 'ERROR').length
    }
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索是实时的，通过 computed 属性过滤
}

const exportLogs = async () => {
  exporting.value = true
  
  try {
    const content = filteredLogs.value
      .map(log => `[${log.timestamp}] [${log.level}] [${log.source}] ${log.message}`)
      .join('\n')
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `openclaw-logs-${new Date().toISOString().substring(0, 10)}.log`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('日志导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshTimer = setInterval(loadLogs, refreshInterval.value * 1000)
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
  }
}

watch(refreshInterval, () => {
  if (autoRefresh.value) {
    clearInterval(refreshTimer)
    refreshTimer = setInterval(loadLogs, refreshInterval.value * 1000)
  }
})

onMounted(() => {
  loadLogs()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.logs-page {
  width: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.log-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.control-left,
.control-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.auto-refresh {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  gap: 10px;
}

.switch-label {
  color: var(--text-secondary);
  font-size: 13px;
}

.log-stats {
  display: flex;
  gap: 20px;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.debug { color: #909399; }
.stat-value.info { color: #67c23a; }
.stat-value.warning { color: #e6a23c; }
.stat-value.error { color: #f56c6c; }

.log-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 0;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border-color);
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.debug { background: color-mix(in srgb, #909399 5%, transparent); }
.log-item.info { background: color-mix(in srgb, #67c23a 5%, transparent); }
.log-item.warning { background: color-mix(in srgb, #e6a23c 5%, transparent); }
.log-item.error { background: color-mix(in srgb, #f56c6c 10%, transparent); }

.log-time {
  color: var(--text-muted);
  white-space: nowrap;
  min-width: 160px;
}

.log-level {
  min-width: 70px;
  font-weight: 600;
}

.log-item.debug .log-level { color: #909399; }
.log-item.info .log-level { color: #67c23a; }
.log-item.warning .log-level { color: #e6a23c; }
.log-item.error .log-level { color: #f56c6c; }

.log-source {
  color: #409eff;
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: var(--text-primary);
  word-break: break-all;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-logs p {
  margin-top: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .log-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-left,
  .control-right {
    justify-content: center;
  }
  
  .log-stats {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .log-item {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
