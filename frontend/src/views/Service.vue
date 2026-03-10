<template>
  <div class="service-page">
    <h2 class="page-title">服务管理</h2>
    
    <!-- 服务状态卡片 -->
    <div class="status-cards">
      <div class="status-card" :class="serviceStatus.status">
        <div class="status-icon">
          <el-icon :size="32">
            <Loading v-if="serviceStatus.status === 'starting'" />
            <SuccessFilled v-else-if="serviceStatus.status === 'running'" />
            <CircleCloseFilled v-else />
          </el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">服务状态</div>
          <div class="status-value">
            {{ serviceStatus.status === 'running' ? '运行中' : serviceStatus.status === 'starting' ? '启动中' : '已停止' }}
          </div>
        </div>
      </div>
      
      <div class="status-card info">
        <div class="status-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">进程 ID</div>
          <div class="status-value">{{ serviceStatus.pid || '-' }}</div>
        </div>
      </div>
      
      <div class="status-card info">
        <div class="status-icon">
          <el-icon :size="32"><Clock /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">运行时间</div>
          <div class="status-value">{{ serviceStatus.uptime || '-' }}</div>
        </div>
      </div>
      
      <div class="status-card info">
        <div class="status-icon">
          <el-icon :size="32"><Coin /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">内存使用</div>
          <div class="status-value">{{ serviceStatus.memory || '-' }}</div>
        </div>
      </div>
    </div>

    <!-- 服务控制 -->
    <div class="card-glow">
      <div class="section-header">
        <h3><el-icon><Operation /></el-icon> 服务控制</h3>
      </div>
      
      <div class="control-panel">
        <div class="control-buttons">
          <el-button 
            type="success" 
            size="large" 
            :loading="actionLoading === 'start'"
            :disabled="serviceStatus.status === 'running'"
            @click="controlService('start')"
          >
            <el-icon><VideoPlay /></el-icon>
            启动服务
          </el-button>
          
          <el-button 
            type="warning" 
            size="large" 
            :loading="actionLoading === 'restart'"
            :disabled="serviceStatus.status !== 'running'"
            @click="controlService('restart')"
          >
            <el-icon><RefreshRight /></el-icon>
            重启服务
          </el-button>
          
          <el-button 
            type="danger" 
            size="large" 
            :loading="actionLoading === 'stop'"
            :disabled="serviceStatus.status !== 'running'"
            @click="controlService('stop')"
          >
            <el-icon><VideoPause /></el-icon>
            停止服务
          </el-button>
        </div>
        
        <div class="auto-start">
          <el-switch v-model="serviceConfig.auto_start" @change="saveAutoStart" />
          <span class="switch-label">开机自动启动</span>
        </div>
      </div>
    </div>

    <!-- 服务配置 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Setting /></el-icon> 服务配置</h3>
        <el-button type="primary" size="small" @click="saveServiceConfig" :loading="savingConfig">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
      
      <div class="config-form">
        <el-form :model="serviceConfig" label-width="150px" class="form-custom">
          <el-form-item label="服务端口">
            <el-input-number v-model="serviceConfig.port" :min="1024" :max="65535" />
          </el-form-item>
          <el-form-item label="日志级别">
            <el-select v-model="serviceConfig.log_level" style="width: 100%">
              <el-option label="DEBUG" value="debug" />
              <el-option label="INFO" value="info" />
              <el-option label="WARNING" value="warning" />
              <el-option label="ERROR" value="error" />
            </el-select>
          </el-form-item>
          <el-form-item label="日志文件路径">
            <el-input v-model="serviceConfig.log_file" placeholder="/var/log/openclaw/openclaw.log" />
          </el-form-item>
          <el-form-item label="数据目录">
            <el-input v-model="serviceConfig.data_dir" placeholder="/data/openclaw" />
          </el-form-item>
          <el-form-item label="最大并发数">
            <el-input-number v-model="serviceConfig.max_concurrent" :min="1" :max="100" />
          </el-form-item>
          <el-form-item label="请求超时(秒)">
            <el-input-number v-model="serviceConfig.timeout" :min="10" :max="300" :step="10" />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 快速命令 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Terminal /></el-icon> 快速命令</h3>
      </div>
      
      <div class="quick-commands">
        <el-button 
          v-for="cmd in quickCommands" 
          :key="cmd.name"
          type="primary" 
          plain
          @click="executeCommand(cmd.command)"
          :loading="executing === cmd.name"
        >
          <el-icon><CaretRight /></el-icon>
          {{ cmd.name }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

const serviceStatus = reactive({
  status: 'stopped', // running, stopped, starting
  pid: null,
  uptime: null,
  memory: null
})

const serviceConfig = reactive({
  port: 8000,
  log_level: 'info',
  log_file: '/var/log/openclaw/openclaw.log',
  data_dir: '/data/openclaw',
  max_concurrent: 10,
  timeout: 60,
  auto_start: false
})

const actionLoading = ref(null)
const savingConfig = ref(false)
const executing = ref(null)
let statusTimer = null

const quickCommands = [
  { name: '查看状态', command: 'status' },
  { name: '查看配置', command: 'config show' },
  { name: '重载配置', command: 'config reload' },
  { name: '清理缓存', command: 'cache clear' },
  { name: '检查更新', command: 'update check' },
  { name: '导出日志', command: 'logs export' }
]

const fetchServiceStatus = async () => {
  try {
    const res = await api.get('/service/status')
    Object.assign(serviceStatus, res.data)
  } catch (error) {
    // ignore
  }
}

const controlService = async (action) => {
  actionLoading.value = action
  try {
    const res = await api.post(`/service/${action}`)
    if (res.data.success) {
      ElMessage.success(action === 'start' ? '服务启动中...' : action === 'stop' ? '服务停止中...' : '服务重启中...')
      // 刷新状态
      setTimeout(fetchServiceStatus, 2000)
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    actionLoading.value = null
  }
}

const saveAutoStart = () => {
  localStorage.setItem('service_auto_start', serviceConfig.auto_start)
  ElMessage.success('自动启动已' + (serviceConfig.auto_start ? '启用' : '禁用'))
}

const saveServiceConfig = async () => {
  savingConfig.value = true
  try {
    localStorage.setItem('service_config', JSON.stringify(serviceConfig))
    ElMessage.success('配置保存成功')
  } finally {
    savingConfig.value = false
  }
}

const executeCommand = async (command) => {
  executing.value = command
  try {
    const res = await api.post('/terminal/execute', { command })
    if (res.data.success) {
      ElMessage.success('命令执行成功')
    } else {
      ElMessage.error(res.data.error || '命令执行失败')
    }
  } catch (error) {
    ElMessage.error('命令执行失败')
  } finally {
    executing.value = null
  }
}

const loadConfig = () => {
  // 加载服务配置
  const saved = localStorage.getItem('service_config')
  if (saved) {
    try {
      Object.assign(serviceConfig, JSON.parse(saved))
    } catch (e) {
      // use defaults
    }
  }
  
  // 加载自动启动设置
  const autoStart = localStorage.getItem('service_auto_start')
  if (autoStart !== null) {
    serviceConfig.auto_start = autoStart === 'true'
  }
}

onMounted(() => {
  loadConfig()
  fetchServiceStatus()
  // 每10秒刷新一次状态
  statusTimer = setInterval(fetchServiceStatus, 10000)
})

onUnmounted(() => {
  if (statusTimer) {
    clearInterval(statusTimer)
  }
})
</script>

<style scoped>
.service-page {
  width: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.status-card.running {
  border-color: var(--success-color);
  background: color-mix(in srgb, var(--success-color) 8%, var(--bg-secondary));
}

.status-card.starting {
  border-color: var(--warning-color);
  background: color-mix(in srgb, var(--warning-color) 8%, var(--bg-secondary));
}

.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.status-card.running .status-icon {
  color: var(--success-color);
}

.status-card.starting .status-icon {
  color: var(--warning-color);
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.control-buttons .el-button {
  min-width: 140px;
}

.auto-start {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.switch-label {
  color: var(--text-secondary);
}

.config-form {
  padding: 0 20px 20px;
}

.quick-commands {
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

@media (max-width: 768px) {
  .status-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .control-buttons .el-button {
    width: 100%;
  }
}
</style>
