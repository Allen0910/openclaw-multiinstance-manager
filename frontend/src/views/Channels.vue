<template>
  <div class="channels-page">
    <h2 class="page-title">消息渠道配置</h2>
    
    <!-- 渠道列表 -->
    <div class="card-glow">
      <div class="section-header">
        <h3><el-icon><Connection /></el-icon> 已配置渠道</h3>
      </div>
      
      <div class="channel-grid">
        <div 
          v-for="channel in channels" 
          :key="channel.id" 
          :class="['channel-card', { active: channel.id === activeChannelId }]"
          @click="selectChannel(channel)"
        >
          <div class="channel-icon" :style="{ background: channel.bg }">
            <span>{{ channel.icon }}</span>
          </div>
          <div class="channel-info">
            <div class="channel-name">{{ channel.name }}</div>
            <div class="channel-status">
              <el-tag v-if="channel.enabled" type="success" size="small">已启用</el-tag>
              <el-tag v-else type="info" size="small">已禁用</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 当前选中渠道配置 -->
    <div class="card-glow" v-if="selectedChannel" style="margin-top: 20px">
      <div class="section-header">
        <h3><el-icon><Setting /></el-icon> {{ selectedChannel.name }} 配置</h3>
        <div class="header-actions">
          <el-button size="small" type="success" @click="testChannel" :loading="testing">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
          <el-button size="small" type="primary" @click="saveChannel" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </div>
      
      <div class="config-form">
        <!-- Telegram 配置 -->
        <template v-if="selectedChannel.id === 'telegram'">
          <el-form :model="telegramConfig" label-width="140px" class="form-custom">
            <el-form-item label="Bot Token">
              <el-input v-model="telegramConfig.bot_token" type="password" show-password placeholder="请输入 Bot Token" />
            </el-form-item>
            <el-form-item label="允许私聊">
              <el-switch v-model="telegramConfig.allow_private" />
            </el-form-item>
            <el-form-item label="允许群组">
              <el-switch v-model="telegramConfig.allow_groups" />
            </el-form-item>
            <el-form-item label="管理员ID">
              <el-input v-model="telegramConfig.admin_ids" placeholder="多个ID用逗号分隔" />
            </el-form-item>
            <el-form-item label="只响应管理员">
              <el-switch v-model="telegramConfig.only_admin" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- 飞书配置 -->
        <template v-else-if="selectedChannel.id === 'feishu'">
          <el-form :model="feishuConfig" label-width="140px" class="form-custom">
            <el-form-item label="App ID">
              <el-input v-model="feishuConfig.app_id" placeholder="请输入 App ID" />
            </el-form-item>
            <el-form-item label="App Secret">
              <el-input v-model="feishuConfig.app_secret" type="password" show-password placeholder="请输入 App Secret" />
            </el-form-item>
            <el-form-item label="Verification Token">
              <el-input v-model="feishuConfig.verification_token" placeholder="请输入 Verification Token" />
            </el-form-item>
            <el-form-item label="加密 Key">
              <el-input v-model="feishuConfig.encrypt_key" type="password" show-password placeholder="可选，加密Key" />
            </el-form-item>
            <el-form-item label="部署区域">
              <el-select v-model="feishuConfig.region" style="width: 100%">
                <el-option label="国内版" value="cn" />
                <el-option label="海外版" value="overseas" />
              </el-select>
            </el-form-item>
          </el-form>
        </template>
        
        <!-- Discord 配置 -->
        <template v-else-if="selectedChannel.id === 'discord'">
          <el-form :model="discordConfig" label-width="140px" class="form-custom">
            <el-form-item label="Bot Token">
              <el-input v-model="discordConfig.bot_token" type="password" show-password placeholder="请输入 Bot Token" />
            </el-form-item>
            <el-form-item label="允许的服务器">
              <el-input v-model="discordConfig.allowed_guilds" placeholder="服务器ID，多个用逗号分隔" />
            </el-form-item>
            <el-form-item label="允许私聊">
              <el-switch v-model="discordConfig.allow_dm" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- Slack 配置 -->
        <template v-else-if="selectedChannel.id === 'slack'">
          <el-form :model="slackConfig" label-width="140px" class="form-custom">
            <el-form-item label="Bot Token">
              <el-input v-model="slackConfig.bot_token" type="password" show-password placeholder="xoxb-xxx" />
            </el-form-item>
            <el-form-item label="App Token">
              <el-input v-model="slackConfig.app_token" type="password" show-password placeholder="xoxb-xxx" />
            </el-form-item>
            <el-form-item label="签名密钥">
              <el-input v-model="slackConfig.signing_secret" placeholder="Slack 签名密钥" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- 微信配置 -->
        <template v-else-if="selectedChannel.id === 'wechat'">
          <el-form :model="wechatConfig" label-width="140px" class="form-custom">
            <el-form-item label="企业ID">
              <el-input v-model="wechatConfig.corp_id" placeholder="企业ID" />
            </el-form-item>
            <el-form-item label="Agent ID">
              <el-input v-model="wechatConfig.agent_id" placeholder="应用Agent ID" />
            </el-form-item>
            <el-form-item label="Secret">
              <el-input v-model="wechatConfig.secret" type="password" show-password placeholder="应用Secret" />
            </el-form-item>
            <el-form-item label="Token">
              <el-input v-model="wechatConfig.token" placeholder="Token" />
            </el-form-item>
            <el-form-item label="Encoding AES Key">
              <el-input v-model="wechatConfig.aes_key" type="password" placeholder="Encoding AES Key" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- 钉钉配置 -->
        <template v-else-if="selectedChannel.id === 'dingtalk'">
          <el-form :model="dingtalkConfig" label-width="140px" class="form-custom">
            <el-form-item label="App Key">
              <el-input v-model="dingtalkConfig.app_key" placeholder="App Key" />
            </el-form-item>
            <el-form-item label="App Secret">
              <el-input v-model="dingtalkConfig.app_secret" type="password" show-password placeholder="App Secret" />
            </el-form-item>
            <el-form-item label="Agent ID">
              <el-input v-model="dingtalkConfig.agent_id" placeholder="Agent ID" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- WhatsApp 配置 -->
        <template v-else-if="selectedChannel.id === 'whatsapp'">
          <el-form :model="whatsappConfig" label-width="140px" class="form-custom">
            <el-form-item label="Phone Number ID">
              <el-input v-model="whatsappConfig.phone_number_id" placeholder="Phone Number ID" />
            </el-form-item>
            <el-form-item label="Access Token">
              <el-input v-model="whatsappConfig.access_token" type="password" show-password placeholder="Access Token" />
            </el-form-item>
            <el-form-item label="Verify Token">
              <el-input v-model="whatsappConfig.verify_token" placeholder="Verify Token" />
            </el-form-item>
          </el-form>
        </template>
        
        <!-- iMessage 配置 -->
        <template v-else-if="selectedChannel.id === 'imessage'">
          <el-form :model="imessageConfig" label-width="140px" class="form-custom">
            <el-form-item label="接收方式">
              <el-select v-model="imessageConfig.receiver_type" style="width: 100%">
                <el-option label="Apple Script" value="applescript" />
                <el-option label="IMacros" value="imacros" />
              </el-select>
            </el-form-item>
            <el-form-item label="接收者ID">
              <el-input v-model="imessageConfig.receiver_id" placeholder="iMessage 接收者邮箱或手机号" />
            </el-form-item>
          </el-form>
        </template>
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
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

// 可用渠道
const allChannels = [
  { id: 'telegram', name: 'Telegram', icon: '✈️', bg: 'linear-gradient(135deg, #0088cc 0%, #005f99 100%)' },
  { id: 'feishu', name: '飞书', icon: '📨', bg: 'linear-gradient(135deg, #4285f4 0%, #1a73e8 100%)' },
  { id: 'discord', name: 'Discord', icon: '🎮', bg: 'linear-gradient(135deg, #5865f2 0%, #4752c4 100%)' },
  { id: 'slack', name: 'Slack', icon: '💬', bg: 'linear-gradient(135deg, #4a154b 0%, #36104a 100%)' },
  { id: 'wechat', name: '微信', icon: '💚', bg: 'linear-gradient(135deg, #07c160 0%, #06ad56 100%)' },
  { id: 'dingtalk', name: '钉钉', icon: '💼', bg: 'linear-gradient(135deg, #0089ff 0%, #0066cc 100%)' },
  { id: 'whatsapp', name: 'WhatsApp', icon: '📱', bg: 'linear-gradient(135deg, #25d366 0%, #128c7e 100%)' },
  { id: 'imessage', name: 'iMessage', icon: '🍎', bg: 'linear-gradient(135deg, #a2aaad 0%, #7d7d7d 100%)' }
]

const channels = ref([])
const activeChannelId = ref(null)
const selectedChannel = ref(null)
const testing = ref(false)
const saving = ref(false)
const testResultVisible = ref(false)
const testResult = ref(null)

// 各渠道配置
const telegramConfig = reactive({
  bot_token: '',
  allow_private: true,
  allow_groups: true,
  admin_ids: '',
  only_admin: false
})

const feishuConfig = reactive({
  app_id: '',
  app_secret: '',
  verification_token: '',
  encrypt_key: '',
  region: 'cn'
})

const discordConfig = reactive({
  bot_token: '',
  allowed_guilds: '',
  allow_dm: true
})

const slackConfig = reactive({
  bot_token: '',
  app_token: '',
  signing_secret: ''
})

const wechatConfig = reactive({
  corp_id: '',
  agent_id: '',
  secret: '',
  token: '',
  aes_key: ''
})

const dingtalkConfig = reactive({
  app_key: '',
  app_secret: '',
  agent_id: ''
})

const whatsappConfig = reactive({
  phone_number_id: '',
  access_token: '',
  verify_token: ''
})

const imessageConfig = reactive({
  receiver_type: 'applescript',
  receiver_id: ''
})

const selectChannel = (channel) => {
  selectedChannel.value = channel
  activeChannelId.value = channel.id
  loadChannelConfig(channel.id)
}

const loadChannelConfig = (channelId) => {
  const saved = localStorage.getItem(`channel_${channelId}`)
  let config
  if (saved) {
    try {
      config = JSON.parse(saved)
    } catch (e) {
      config = {}
    }
  } else {
    config = {}
  }
  
  // 根据渠道类型加载对应配置
  switch (channelId) {
    case 'telegram':
      Object.assign(telegramConfig, { bot_token: '', allow_private: true, allow_groups: true, admin_ids: '', only_admin: false, ...config })
      break
    case 'feishu':
      Object.assign(feishuConfig, { app_id: '', app_secret: '', verification_token: '', encrypt_key: '', region: 'cn', ...config })
      break
    case 'discord':
      Object.assign(discordConfig, { bot_token: '', allowed_guilds: '', allow_dm: true, ...config })
      break
    case 'slack':
      Object.assign(slackConfig, { bot_token: '', app_token: '', signing_secret: '', ...config })
      break
    case 'wechat':
      Object.assign(wechatConfig, { corp_id: '', agent_id: '', secret: '', token: '', aes_key: '', ...config })
      break
    case 'dingtalk':
      Object.assign(dingtalkConfig, { app_key: '', app_secret: '', agent_id: '', ...config })
      break
    case 'whatsapp':
      Object.assign(whatsappConfig, { phone_number_id: '', access_token: '', verify_token: '', ...config })
      break
    case 'imessage':
      Object.assign(imessageConfig, { receiver_type: 'applescript', receiver_id: '', ...config })
      break
  }
}

const getCurrentConfig = () => {
  switch (selectedChannel.value?.id) {
    case 'telegram': return telegramConfig
    case 'feishu': return feishuConfig
    case 'discord': return discordConfig
    case 'slack': return slackConfig
    case 'wechat': return wechatConfig
    case 'dingtalk': return dingtalkConfig
    case 'whatsapp': return whatsappConfig
    case 'imessage': return imessageConfig
    default: return {}
  }
}

const testChannel = async () => {
  testing.value = true
  testResult.value = null
  testResultVisible.value = true
  
  try {
    const res = await api.post('/channels/test', {
      channel: selectedChannel.value.id,
      config: getCurrentConfig()
    })
    testResult.value = {
      success: res.data.success,
      message: res.data.message || (res.data.success ? '连接成功' : '连接失败')
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: '测试请求失败'
    }
  } finally {
    testing.value = false
  }
}

const saveChannel = () => {
  saving.value = true
  try {
    localStorage.setItem(`channel_${selectedChannel.value.id}`, JSON.stringify(getCurrentConfig()))
    
    // 更新启用状态
    const idx = channels.value.findIndex(c => c.id === selectedChannel.value.id)
    if (idx >= 0) {
      channels.value[idx].enabled = true
    }
    
    ElMessage.success('渠道配置保存成功')
  } finally {
    saving.value = false
  }
}

const loadChannels = () => {
  const saved = localStorage.getItem('channels')
  if (saved) {
    try {
      channels.value = JSON.parse(saved)
    } catch (e) {
      channels.value = [allChannels[0], allChannels[1]]
    }
  } else {
    channels.value = [allChannels[0], allChannels[1]]
  }
  
  if (channels.value.length > 0) {
    selectChannel(channels.value[0])
  }
}

onMounted(() => {
  loadChannels()
})
</script>

<style scoped>
.channels-page {
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

.channel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  padding: 0 20px 20px;
}

.channel-card {
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

.channel-card:hover {
  border-color: var(--accent-color);
}

.channel-card.active {
  border-color: var(--accent-color);
  background: color-mix(in srgb, var(--accent-color) 8%, var(--bg-secondary));
}

.channel-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.channel-info {
  flex: 1;
}

.channel-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.channel-status {
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
</style>
