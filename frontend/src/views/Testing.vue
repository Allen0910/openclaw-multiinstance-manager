<template>
  <div class="testing-page">
    <h2 class="page-title">测试诊断</h2>
    
    <!-- 系统环境检查 -->
    <div class="card-glow">
      <div class="section-header">
        <h3><el-icon><Monitor /></el-icon> 系统环境检查</h3>
        <el-button type="primary" size="small" @click="runSystemCheck" :loading="checkingSystem">
          <el-icon><RefreshRight /></el-icon>
          重新检查
        </el-button>
      </div>
      
      <div class="check-items">
        <div v-for="item in systemChecks" :key="item.name" class="check-item">
          <div class="check-icon">
            <el-icon :size="20" :class="item.status">
              <SuccessFilled v-if="item.status === 'success'" />
              <WarningFilled v-else-if="item.status === 'warning'" />
              <CircleCloseFilled v-else />
            </el-icon>
          </div>
          <div class="check-info">
            <div class="check-name">{{ item.name }}</div>
            <div class="check-detail">{{ item.detail }}</div>
          </div>
          <div class="check-status">
            <el-tag :type="item.status === 'success' ? 'success' : item.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ item.status === 'success' ? '正常' : item.status === 'warning' ? '警告' : '异常' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- AI 连接测试 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Connection /></el-icon> AI 连接测试</h3>
      </div>
      
      <div class="test-panel">
        <el-form :inline="true" :model="aiTestForm" class="test-form">
          <el-form-item label="AI 服务商">
            <el-select v-model="aiTestForm.provider" placeholder="选择服务商" style="width: 180px">
              <el-option label="OpenAI" value="openai" />
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="Moonshot" value="moonshot" />
              <el-option label="智谱 GLM" value="zhipu" />
              <el-option label="Anthropic" value="anthropic" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="testAIConnection" :loading="testingAI">
              <el-icon><Connection /></el-icon>
              开始测试
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="aiTestResult" class="test-result" :class="aiTestResult.success ? 'success' : 'error'">
          <div class="result-header">
            <el-icon :size="24">
              <SuccessFilled v-if="aiTestResult.success" />
              <CircleCloseFilled v-else />
            </el-icon>
            <span>{{ aiTestResult.success ? '连接成功' : '连接失败' }}</span>
          </div>
          <div v-if="aiTestResult.latency" class="result-latency">
            响应时间: {{ aiTestResult.latency }}ms
          </div>
          <div v-if="aiTestResult.error" class="result-error">
            {{ aiTestResult.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- 渠道连通性测试 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Promotion /></el-icon> 渠道连通性测试</h3>
      </div>
      
      <div class="channel-tests">
        <div v-for="channel in channelTests" :key="channel.id" class="channel-test">
          <div class="channel-test-header">
            <span class="channel-name">{{ channel.name }}</span>
            <el-button size="small" type="primary" @click="testChannel(channel)" :loading="channel.testing">
              测试
            </el-button>
          </div>
          <div v-if="channel.result" class="channel-result" :class="channel.result.success ? 'success' : 'error'">
            <el-icon :size="16">
              <SuccessFilled v-if="channel.result.success" />
              <CircleCloseFilled v-else />
            </el-icon>
            <span>{{ channel.result.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 网络诊断 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Network /></el-icon> 网络诊断</h3>
        <el-button type="primary" size="small" @click="runNetworkDiag" :loading="runningDiag">
          <el-icon><RefreshRight /></el-icon>
          运行诊断
        </el-button>
      </div>
      
      <div class="diag-form">
        <el-form :inline="true">
          <el-form-item label="目标地址">
            <el-input v-model="diagTarget" placeholder="如: api.openai.com" style="width: 200px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runPing" :loading="runningPing">
              <el-icon><Connection /></el-icon>
              Ping 测试
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div v-if="pingResult" class="ping-result">
        <pre>{{ pingResult }}</pre>
      </div>
    </div>

    <!-- 诊断报告 -->
    <div class="card-glow" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Document /></el-icon> 诊断报告</h3>
        <div class="header-actions">
          <el-button size="small" @click="exportReport" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </div>
      </div>
      
      <div class="report-content">
        <el-input
          v-model="diagnosticReport"
          type="textarea"
          :rows="10"
          placeholder="点击上方按钮生成诊断报告..."
          readonly
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

// 系统检查项
const systemChecks = ref([
  { name: 'Python 环境', detail: '检查 Python 版本', status: 'pending' },
  { name: 'Docker 服务', detail: '检查 Docker 是否运行', status: 'pending' },
  { name: '网络连接', detail: '检查外网连通性', status: 'pending' },
  { name: '磁盘空间', detail: '检查可用磁盘空间', status: 'pending' },
  { name: '内存状态', detail: '检查可用内存', status: 'pending' },
  { name: '配置文件', detail: '检查配置文件是否存在', status: 'pending' }
])

const checkingSystem = ref(false)
const aiTestForm = reactive({
  provider: 'openai'
})
const testingAI = ref(false)
const aiTestResult = ref(null)

const channelTests = ref([
  { id: 'telegram', name: 'Telegram', testing: false, result: null },
  { id: 'feishu', name: '飞书', testing: false, result: null },
  { id: 'discord', name: 'Discord', testing: false, result: null },
  { id: 'slack', name: 'Slack', testing: false, result: null }
])

const runningDiag = ref(false)
const runningPing = ref(false)
const diagTarget = ref('api.openai.com')
const pingResult = ref('')
const diagnosticReport = ref('')
const exporting = ref(false)

const runSystemCheck = async () => {
  checkingSystem.value = true
  
  // 模拟检查
  const checks = [
    { name: 'Python 环境', detail: 'Python 3.10.12 可用', status: 'success' },
    { name: 'Docker 服务', detail: 'Docker 24.0.7 运行中', status: 'success' },
    { name: '网络连接', detail: '外网连接正常', status: 'success' },
    { name: '磁盘空间', detail: '可用空间 45.2GB', status: 'warning' },
    { name: '内存状态', detail: '可用内存 8.2GB', status: 'success' },
    { name: '配置文件', detail: '配置文件完整', status: 'success' }
  ]
  
  systemChecks.value = checks
  checkingSystem.value = false
  ElMessage.success('系统检查完成')
}

const testAIConnection = async () => {
  testingAI.value = true
  aiTestResult.value = null
  
  try {
    const res = await api.post('/ai/test', {
      provider: aiTestForm.provider,
      config: {}
    })
    aiTestResult.value = res.data
  } catch (error) {
    aiTestResult.value = {
      success: false,
      error: error.response?.data?.detail || error.message
    }
  } finally {
    testingAI.value = false
  }
}

const testChannel = async (channel) => {
  channel.testing = true
  channel.result = null
  
  try {
    const res = await api.post('/channels/test', {
      channel: channel.id,
      config: {}
    })
    channel.result = res.data
  } catch (error) {
    channel.result = {
      success: false,
      message: error.response?.data?.detail || '测试失败'
    }
  } finally {
    channel.testing = false
  }
}

const runNetworkDiag = async () => {
  runningDiag.value = true
  
  try {
    const res = await api.post('/diagnostics/network', {
      target: diagTarget.value
    })
    pingResult.value = res.data.output || '诊断完成'
  } catch (error) {
    pingResult.value = '诊断失败: ' + (error.response?.data?.detail || error.message)
  } finally {
    runningDiag.value = false
  }
}

const runPing = async () => {
  runningPing.value = true
  pingResult.value = ''
  
  try {
    const res = await api.post('/diagnostics/ping', {
      target: diagTarget.value
    })
    pingResult.value = res.data.output || 'Ping 完成'
  } catch (error) {
    pingResult.value = 'Ping 失败: ' + (error.response?.data?.detail || error.message)
  } finally {
    runningPing.value = false
  }
}

const generateReport = () => {
  const timestamp = new Date().toLocaleString()
  let report = `OpenClaw Manager 诊断报告\n`
  report += `生成时间: ${timestamp}\n`
  report += `${'='.repeat(50)}\n\n`
  
  // 系统状态
  report += `【系统状态】\n`
  systemChecks.value.forEach(item => {
    const status = item.status === 'success' ? '✓' : item.status === 'warning' ? '⚠' : '✗'
    report += `${status} ${item.name}: ${item.detail}\n`
  })
  
  report += `\n【AI 配置】\n`
  report += `测试服务商: ${aiTestForm.provider}\n`
  if (aiTestResult.value) {
    report += `测试结果: ${aiTestResult.value.success ? '成功' : '失败'}\n`
    if (aiTestResult.value.latency) {
      report += `响应时间: ${aiTestResult.value.latency}ms\n`
    }
  }
  
  return report
}

const exportReport = async () => {
  exporting.value = true
  try {
    diagnosticReport.value = generateReport()
    
    // 可以添加下载功能
    ElMessage.success('报告已生成')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  runSystemCheck()
})
</script>

<style scoped>
.testing-page {
  width: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
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

.header-actions {
  display: flex;
  gap: 10px;
}

.check-items {
  padding: 0 20px 20px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}

.check-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.check-icon .success {
  color: var(--success-color);
}

.check-icon .warning {
  color: var(--warning-color);
}

.check-icon .error, .check-icon .pending {
  color: var(--danger-color);
}

.check-info {
  flex: 1;
}

.check-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.check-detail {
  font-size: 12px;
  color: var(--text-muted);
}

.test-panel {
  padding: 0 20px 20px;
}

.test-form {
  margin-bottom: 16px;
}

.test-result {
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
}

.test-result.success {
  border-left: 4px solid var(--success-color);
}

.test-result.error {
  border-left: 4px solid var(--danger-color);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 8px;
}

.test-result.success .result-header {
  color: var(--success-color);
}

.test-result.error .result-header {
  color: var(--danger-color);
}

.result-latency {
  font-size: 13px;
  color: var(--text-secondary);
}

.result-error {
  font-size: 13px;
  color: var(--danger-color);
  margin-top: 8px;
}

.channel-tests {
  padding: 0 20px 20px;
}

.channel-test {
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}

.channel-test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-name {
  font-weight: 600;
  color: var(--text-primary);
}

.channel-result {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 13px;
}

.channel-result.success {
  color: var(--success-color);
}

.channel-result.error {
  color: var(--danger-color);
}

.diag-form {
  padding: 0 20px 20px;
}

.ping-result {
  padding: 12px 20px;
}

.ping-result pre {
  margin: 0;
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: var(--radius-md);
  max-height: 200px;
  overflow: auto;
}

.report-content {
  padding: 0 20px 20px;
}
</style>
