<template>
  <div class="ai-config-page">
    <h2 class="page-title">AI 配置</h2>
    
    <!-- AI 服务商列表 -->
    <div class="card-glow">
      <div class="section-header">
        <h3><el-icon><Connection /></el-icon> AI 服务商</h3>
        <el-button type="primary" size="small" class="btn-primary" @click="addProvider">
          <el-icon><Plus /></el-icon>
          添加服务商
        </el-button>
      </div>
      
      <div class="provider-grid">
        <div 
          v-for="provider in providers" 
          :key="provider.id" 
          :class="['provider-card', { active: provider.id === activeProviderId }]"
          @click="selectProvider(provider)"
        >
          <div class="provider-icon" :style="{ background: provider.bg }">
            <span>{{ provider.name.substring(0, 2) }}</span>
          </div>
          <div class="provider-info">
            <div class="provider-name">{{ provider.name }}</div>
            <div class="provider-status">
              <el-tag v-if="provider.enabled" type="success" size="small">已启用</el-tag>
              <el-tag v-else type="info" size="small">已禁用</el-tag>
            </div>
          </div>
          <el-switch 
            v-model="provider.enabled" 
            @change="toggleProvider(provider)"
            @click.stop
          />
        </div>
      </div>
    </div>

    <!-- 当前选中服务商配置 -->
    <div class="card-glow" v-if="selectedProvider" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Setting /></el-icon> {{ selectedProvider.name }} 配置</h3>
        <div class="header-actions">
          <el-button size="small" type="success" @click="testConnection" :loading="testing">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
          <el-button size="small" type="primary" @click="saveProvider" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </div>
      
      <div class="config-form">
        <el-form :model="providerConfig" label-width="140px" class="form-custom">
          <el-form-item label="API 密钥">
            <el-input 
              v-model="providerConfig.api_key" 
              type="password" 
              show-password 
              placeholder="请输入 API Key"
            />
          </el-form-item>
          <el-form-item label="API 地址">
            <el-input 
              v-model="providerConfig.api_base" 
              placeholder="如: https://api.openai.com/v1"
            />
          </el-form-item>
          <el-form-item label="模型名称">
            <el-select v-model="providerConfig.model" placeholder="选择模型" style="width: 100%">
              <el-option 
                v-for="model in selectedProvider.models" 
                :key="model" 
                :label="model" 
                :value="model"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="自定义模型">
            <el-input 
              v-model="providerConfig.custom_model" 
              placeholder="如需使用其他模型，请输入模型名称"
            />
          </el-form-item>
          <el-form-item label="最大 Token">
            <el-input-number v-model="providerConfig.max_tokens" :min="100" :max="100000" :step="100" />
          </el-form-item>
          <el-form-item label="Temperature">
            <el-slider v-model="providerConfig.temperature" :min="0" :max="2" :step="0.1" :format-tooltip="val => val.toFixed(1)" />
          </el-form-item>
          <el-form-item label="代理地址">
            <el-input 
              v-model="providerConfig.proxy" 
              placeholder="可选，如: http://127.0.0.1:7890"
            />
          </el-form-item>
          <el-form-item label="设为默认模型">
            <el-switch v-model="providerConfig.is_default" />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 测试结果 -->
    <el-dialog v-model="testResultVisible" title="连接测试结果" width="500px" class="dialog-custom">
      <div v-if="testResult" :class="['test-result', testResult.success ? 'success' : 'error']">
        <el-icon :size="48">
          <SuccessFilled v-if="testResult.success" />
          <CircleCloseFilled v-else />
        </el-icon>
        <div class="test-message">{{ testResult.message }}</div>
        <div v-if="testResult.details" class="test-details">
          <pre>{{ testResult.details }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 添加服务商对话框 -->
    <el-dialog v-model="addProviderVisible" title="添加 AI 服务商" width="400px" class="dialog-custom">
      <el-form :model="newProvider" label-width="100px">
        <el-form-item label="服务商">
          <el-select v-model="newProvider.name" placeholder="选择服务商" style="width: 100%">
            <el-option 
              v-for="p in availableProviders" 
              :key="p.id" 
              :label="p.name" 
              :value="p.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addProviderVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddProvider">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

// 可用的 AI 服务商
const allProviders = [
  { id: 'openai', name: 'OpenAI', bg: 'linear-gradient(135deg, #10a37f 0%, #1a7f5a 100%)', models: ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'] },
  { id: 'anthropic', name: 'Anthropic', bg: 'linear-gradient(135deg, #d4a373 0%, #bc6c25 100%)', models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'] },
  { id: 'deepseek', name: 'DeepSeek', bg: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', models: ['deepseek-chat', 'deepseek-coder'] },
  { id: 'moonshot', name: 'Moonshot', bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'] },
  { id: 'zhipu', name: '智谱 GLM', bg: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)', models: ['glm-4', 'glm-4-flash', 'glm-4-plus', 'glm-3-turbo'] },
  { id: 'gemini', name: 'Google Gemini', bg: 'linear-gradient(135deg, #4285f4 0%, #1a73e8 100%)', models: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-pro-exp-0801'] },
  { id: 'azure', name: 'Azure OpenAI', bg: 'linear-gradient(135deg, #0078d4 0%, #005a9e 100%)', models: ['gpt-4', 'gpt-4-turbo', 'gpt-35-turbo'] },
  { id: 'ollama', name: 'Ollama', bg: 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)', models: ['llama2', 'mistral', 'codellama', 'orca-mini'] },
  { id: 'qianfan', name: '百度千帆', bg: 'linear-gradient(135deg, #2932e1 0%, #1e1eb8 100%)', models: ['ernie-4.0-8k', 'ernie-3.5-8k', 'ernie-speed-8k'] },
  { id: 'tongyi', name: '阿里通义', bg: 'linear-gradient(135deg, #ff6a00 0%, #e55a00 100%)', models: ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-max-longcontext'] },
  { id: 'spark', name: '讯飞星火', bg: 'linear-gradient(135deg, #00c7f2 0%, #0099b3 100%)', models: ['spark-v3.5', 'spark-v3.0', 'spark-v2.0'] },
  { id: 'siliconflow', name: 'SiliconFlow', bg: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)', models: ['Qwen/Qwen2-72B-Instruct', 'THUDM/glm-4-9b-chat'] },
  { id: 'minimax', name: 'MiniMax', bg: 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)', models: ['abab6.5s-chat', 'abab6.5g-chat'] },
  { id: 'custom', name: '自定义', bg: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)', models: [] }
]

const providers = ref([])
const activeProviderId = ref(null)
const selectedProvider = ref(null)
const providerConfig = reactive({
  api_key: '',
  api_base: '',
  model: '',
  custom_model: '',
  max_tokens: 4096,
  temperature: 0.7,
  proxy: '',
  is_default: false
})

const testing = ref(false)
const saving = ref(false)
const testResultVisible = ref(false)
const testResult = ref(null)
const addProviderVisible = ref(false)
const newProvider = reactive({ name: '' })

const availableProviders = computed(() => {
  const existingIds = providers.value.map(p => p.id)
  return allProviders.filter(p => !existingIds.includes(p.id))
})

const selectProvider = (provider) => {
  selectedProvider.value = provider
  activeProviderId.value = provider.id
  // 加载配置
  const saved = localStorage.getItem(`ai_provider_${provider.id}`)
  if (saved) {
    try {
      Object.assign(providerConfig, JSON.parse(saved))
    } catch (e) {
      // use defaults
    }
  } else {
    Object.assign(providerConfig, {
      api_key: '',
      api_base: provider.id === 'ollama' ? 'http://localhost:11434' : '',
      model: provider.models[0] || '',
      custom_model: '',
      max_tokens: 4096,
      temperature: 0.7,
      proxy: '',
      is_default: provider.id === 'openai'
    })
  }
}

const toggleProvider = (provider) => {
  ElMessage.success(`${provider.name} 已${provider.enabled ? '启用' : '禁用'}`)
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  testResultVisible.value = true
  
  try {
    const res = await api.post('/ai/test', {
      provider: selectedProvider.value.id,
      config: providerConfig
    })
    testResult.value = {
      success: res.data.success,
      message: res.data.message || (res.data.success ? '连接成功' : '连接失败'),
      details: res.data.details
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: '测试请求失败',
      details: error?.response?.data?.detail || error.message
    }
  } finally {
    testing.value = false
  }
}

const saveProvider = () => {
  saving.value = true
  try {
    localStorage.setItem(`ai_provider_${selectedProvider.value.id}`, JSON.stringify(providerConfig))
    
    // 更新 providers 列表
    const idx = providers.value.findIndex(p => p.id === selectedProvider.value.id)
    if (idx >= 0) {
      providers.value[idx].enabled = providerConfig.is_default ? true : providers.value[idx].enabled
    }
    
    ElMessage.success('配置保存成功')
  } finally {
    saving.value = false
  }
}

const addProvider = () => {
  newProvider.name = ''
  addProviderVisible.value = true
}

const confirmAddProvider = () => {
  if (!newProvider.name) {
    ElMessage.warning('请选择服务商')
    return
  }
  
  const provider = allProviders.find(p => p.id === newProvider.name)
  if (provider) {
    providers.value.push({ ...provider, enabled: false })
    addProviderVisible.value = false
    ElMessage.success(`已添加 ${provider.name}`)
  }
}

const loadProviders = () => {
  // 从 localStorage 加载所有已配置的服务商
  const saved = localStorage.getItem('ai_providers')
  if (saved) {
    try {
      providers.value = JSON.parse(saved)
    } catch (e) {
      providers.value = [...allProviders.slice(0, 4)] // 默认4个
    }
  } else {
    providers.value = [
      allProviders[0], // OpenAI
      allProviders[2], // DeepSeek
      allProviders[3], // Moonshot
      allProviders[4]  // 智谱
    ]
  }
  
  // 选中第一个
  if (providers.value.length > 0) {
    selectProvider(providers.value[0])
  }
}

onMounted(() => {
  loadProviders()
})
</script>

<style scoped>
.ai-config-page {
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

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  padding: 0 20px 20px;
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.provider-card:hover {
  border-color: var(--accent-color);
}

.provider-card.active {
  border-color: var(--accent-color);
  background: color-mix(in srgb, var(--accent-color) 8%, var(--bg-secondary));
}

.provider-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 14px;
}

.provider-info {
  flex: 1;
}

.provider-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.provider-status {
  font-size: 12px;
}

.config-form {
  padding: 0 20px 20px;
}

.test-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  text-align: center;
}

.test-result.success {
  color: var(--success-color);
}

.test-result.error {
  color: var(--danger-color);
}

.test-message {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0;
}

.test-details {
  width: 100%;
  text-align: left;
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: var(--radius-md);
  max-height: 200px;
  overflow: auto;
}

.test-details pre {
  margin: 0;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
