<template>
  <div class="jarvis-container">
    <!-- 全息背景网格 -->
    <div class="holographic-grid"></div>
    
    <!-- 3D 弧形反应堆 -->
    <div class="arc-reactor">
      <!-- 外圈 -->
      <div class="reactor-ring outer">
        <div class="ring-glow"></div>
      </div>
      <!-- 中圈 -->
      <div class="reactor-ring middle">
        <div class="ring-glow"></div>
      </div>
      <!-- 内圈 -->
      <div class="reactor-ring inner">
        <div class="ring-glow"></div>
      </div>
      <!-- 核心 -->
      <div class="reactor-core">
        <div class="core-pulse"></div>
        <div class="core-inner"></div>
      </div>
      <!-- 能量流动画 -->
      <div class="energy-flow"></div>
    </div>

    <!-- 3D 全息面板 -->
    <div class="holographic-panels">
      <!-- 左侧面板 - 系统状态 -->
      <div class="holo-panel left">
        <div class="panel-header">
          <span class="panel-title">SYSTEMS</span>
          <span class="panel-status online">ONLINE</span>
        </div>
        <div class="panel-content">
          <div class="system-item" v-for="(sys, index) in systems" :key="index">
            <div class="sys-name">{{ sys.name }}</div>
            <div class="sys-bar">
              <div class="sys-value" :style="{ width: sys.value + '%', background: sys.color }"></div>
            </div>
            <div class="sys-value-text">{{ sys.value }}%</div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 - 时间显示 -->
      <div class="holo-panel right">
        <div class="panel-header">
          <span class="panel-title">TIMELINE</span>
        </div>
        <div class="panel-content time-display">
          <div class="time-main">{{ currentTime }}</div>
          <div class="date-display">{{ currentDate }}</div>
          <div class="weekday">{{ weekday }}</div>
        </div>
      </div>
    </div>

    <!-- 中央核心显示 -->
    <div class="core-display">
      <div class="core-avatar">
        <svg viewBox="0 0 100 100" class="avatar-svg">
          <!-- 外圈 -->
          <circle cx="50" cy="50" r="48" fill="none" stroke="#00e5cc" stroke-width="1" opacity="0.5"/>
          <circle cx="50" cy="50" r="45" fill="none" stroke="#00e5cc" stroke-width="0.5" opacity="0.3"/>
          <!-- 内圈 -->
          <circle cx="50" cy="50" r="35" fill="none" stroke="#00e5cc" stroke-width="1" opacity="0.7"/>
          <circle cx="50" cy="50" r="25" fill="none" stroke="#00e5cc" stroke-width="0.5"/>
          <!-- 核心 -->
          <circle cx="50" cy="50" r="15" fill="rgba(0, 229, 204, 0.3)"/>
          <circle cx="50" cy="50" r="8" fill="#00e5cc">
            <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
          </circle>
          <!-- 装饰线 -->
          <line x1="50" y1="2" x2="50" y2="15" stroke="#00e5cc" stroke-width="1" opacity="0.5"/>
          <line x1="50" y1="85" x2="50" y2="98" stroke="#00e5cc" stroke-width="1" opacity="0.5"/>
          <line x1="2" y1="50" x2="15" y2="50" stroke="#00e5cc" stroke-width="1" opacity="0.5"/>
          <line x1="85" y1="50" x2="98" y2="50" stroke="#00e5cc" stroke-width="1" opacity="0.5"/>
        </svg>
      </div>
      <div class="core-status">
        <div class="status-indicator" :class="{ active: isListening }"></div>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>

    <!-- 语音波形可视化 -->
    <div class="waveform-section">
      <canvas ref="waveformCanvas" class="waveform-canvas"></canvas>
      <div class="waveform-label" v-if="isListening">LISTENING...</div>
      <div class="waveform-label" v-else-if="isProcessing">PROCESSING...</div>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <!-- 主语音按钮 -->
      <button 
        class="voice-btn" 
        :class="{ listening: isListening, processing: isProcessing, speaking: isSpeaking }"
        @mousedown="startVoiceInput"
        @mouseup="stopVoiceInput"
        @mouseleave="stopVoiceInput"
      >
        <div class="btn-outer-ring"></div>
        <div class="btn-middle-ring"></div>
        <div class="btn-inner">
          <div class="btn-core">
            <svg v-if="!isListening && !isProcessing" viewBox="0 0 24 24" class="mic-icon">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
            <div v-else class="voice-waves">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </button>

      <!-- 功能按钮组 -->
      <div class="action-buttons">
        <button class="action-btn" @click="speakCurrentText" title="语音播报">
          <svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
        </button>
        <button class="action-btn" @click="showSystemInfo" title="系统信息">
          <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/></svg>
        </button>
        <button class="action-btn" @click="clearConversation" title="清空对话">
          <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
        <button class="action-btn" :class="{ active: voiceEnabled }" @click="toggleVoice" title="开关语音">
          <svg v-if="voiceEnabled" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
          <svg v-else viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
        </button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-container">
        <div class="input-glow"></div>
        <input 
          v-model="inputText" 
          type="text" 
          class="jarvis-input"
          placeholder="输入指令或消息..."
          @keyup.enter="sendMessage"
        />
        <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim()">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>

    <!-- 对话显示区域 -->
    <div class="conversation-area" ref="conversationArea">
      <div 
        v-for="(msg, index) in conversation" 
        :key="index" 
        class="message"
        :class="msg.role"
      >
        <div class="message-avatar">
          <svg v-if="msg.role === 'jarvis'" viewBox="0 0 24 24" class="jarvis-avatar">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1"/>
            <circle cx="12" cy="12" r="6" fill="none" stroke="currentColor" stroke-width="1"/>
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" class="user-avatar">
            <circle cx="12" cy="8" r="4" fill="currentColor"/>
            <path d="M12 14c-4 0-8 2-8 4v2h16v-2c0-2-4-4-8-4z" fill="currentColor"/>
          </svg>
        </div>
        <div class="message-content">
          <div class="message-text">{{ msg.content }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="status-bar">
      <div class="status-item">
        <span class="status-dot online"></span>
        <span>贾维斯在线</span>
      </div>
      <div class="status-item">
        <span class="status-label">语音</span>
        <span :class="voiceEnabled ? 'status-on' : 'status-off'">{{ voiceEnabled ? '启用' : '禁用' }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">连接</span>
        <span class="status-on">已连接</span>
      </div>
    </div>

    <!-- 装饰性数据流 -->
    <div class="decorative-streams">
      <div class="stream-column" v-for="i in 8" :key="i" :style="{ '--delay': i * 0.3 + 's', '--x': (i * 12.5) + '%' }">
        <div class="stream-content">
          <span v-for="j in 30" :key="j">{{ randomChar() }}</span>
        </div>
      </div>
    </div>

    <!-- 扫描线效果 -->
    <div class="scanline"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

// 状态变量
const isListening = ref(false)
const isProcessing = ref(false)
const isSpeaking = ref(false)
const voiceEnabled = ref(true)
const inputText = ref('')
const statusText = ref('等待指令')
const conversation = ref([])
const conversationArea = ref(null)
const waveformCanvas = ref(null)

// 系统状态数据
const systems = ref([
  { name: '反应堆', value: 98, color: '#00e5cc' },
  { name: '装甲', value: 100, color: '#00e5cc' },
  { name: '人工智能', value: 100, color: '#00e5cc' },
  { name: '通信', value: 95, color: '#00e5cc' },
  { name: '防御', value: 100, color: '#00e5cc' },
  { name: '能源', value: 92, color: '#00e5cc' },
])

// 时间计算
const currentTime = ref('')
const currentDate = ref('')
const weekday = ref('')

const updateTime = () => {
  const now = new Date()
  currentTime.value = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  currentDate.value = `${now.getFullYear()}年${(now.getMonth() + 1).toString().padStart(2, '0')}月${now.getDate().toString().padStart(2, '0')}日`
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  weekday.value = weekdays[now.getWeekday()]
}

// 语音识别和合成
let recognition = null
let synthesis = null
let animationFrame = null
let timeInterval = null

// 初始化
onMounted(() => {
  initSpeechRecognition()
  initSpeechSynthesis()
  initWaveform()
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  // 模拟系统启动动画
  setTimeout(() => {
    statusText.value = '系统就绪'
    setTimeout(() => {
      statusText.value = '等待指令'
    }, 1500)
  }, 1000)
  
  // 添加欢迎消息
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'jarvis',
    content: '您好，先生。我是贾维斯，为您服务。',
    time
  })
  
  //欢迎 延迟播放语音
  setTimeout(() => {
    if (voiceEnabled.value) {
      speak('您好，先生。我是贾维斯，为您服务。')
    }
  }, 2000)
})

onBeforeUnmount(() => {
  if (recognition) {
    recognition.stop()
  }
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (synthesis) {
    synthesis.cancel()
  }
})

// 监听对话变化，自动滚动到底部
watch(conversation.value, () => {
  nextTick(() => {
    if (conversationArea.value) {
      conversationArea.value.scrollTop = conversationArea.value.scrollHeight
    }
  })
})

// 初始化语音识别
const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('语音识别不支持')
    ElMessage.warning('您的浏览器不支持语音识别功能')
    return
  }
  
  recognition = new SpeechRecognition()
  recognition.continuous = false
  recognition.interimResults = true
  recognition.lang = 'zh-CN'
  
  recognition.onstart = () => {
    isListening.value = true
    statusText.value = '正在监听...'
  }
  
  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join('')
    
    if (event.results[0].isFinal) {
      handleVoiceInput(transcript)
    }
  }
  
  recognition.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    isListening.value = false
    statusText.value = '识别失败'
    if (event.error !== 'no-speech') {
      ElMessage.error('语音识别出错，请重试')
    }
  }
  
  recognition.onend = () => {
    isListening.value = false
    if (statusText.value === '正在监听...') {
      statusText.value = '等待指令'
    }
  }
}

// 初始化语音合成
const initSpeechSynthesis = () => {
  if (!window.speechSynthesis) {
    console.warn('语音合成不支持')
    return
  }
  synthesis = window.speechSynthesis
  
  // 尝试设置更自然的语音
  const voices = synthesis.getVoices()
  // 优先选择英文语音（贾维斯的标志性声音）
  const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('English'))
  if (englishVoice) {
    // 保存选中的语音
  }
}

// 语音输入
const startVoiceInput = () => {
  if (!recognition) {
    ElMessage.warning('您的浏览器不支持语音识别')
    return
  }
  try {
    recognition.start()
  } catch (e) {
    console.error('启动语音识别失败:', e)
  }
}

const stopVoiceInput = () => {
  if (recognition && isListening.value) {
    recognition.stop()
  }
}

// 处理语音输入
const handleVoiceInput = (text) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'user',
    content: text,
    time
  })
  
  processJarvisResponse(text)
}

// 发送消息
const sendMessage = () => {
  const text = inputText.value.trim()
  if (!text) return
  
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'user',
    content: text,
    time
  })
  
  inputText.value = ''
  processJarvisResponse(text)
}

// 处理贾维斯响应
const processJarvisResponse = async (text) => {
  isProcessing.value = true
  statusText.value = '处理中...'
  
  try {
    // 调用后端 API 获取响应
    const res = await api.post('/ai/chat', {
      message: text,
      context: conversation.value.slice(-5)
    })
    
    const response = res.data.response || res.data.message || '抱歉，我未能理解您的指令。'
    
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    conversation.value.push({
      role: 'jarvis',
      content: response,
      time
    })
    
    if (voiceEnabled.value) {
      speak(response)
    }
    
  } catch (error) {
    console.error('API 调用失败:', error)
    // 如果后端 API 失败，使用本地响应
    const localResponse = generateLocalResponse(text)
    
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    conversation.value.push({
      role: 'jarvis',
      content: localResponse,
      time
    })
    
    if (voiceEnabled.value) {
      speak(localResponse)
    }
  } finally {
    isProcessing.value = false
    statusText.value = '等待指令'
  }
}

// 生成本地响应
const generateLocalResponse = (text) => {
  const lowerText = text.toLowerCase()
  
  if (lowerText.includes('hello') || lowerText.includes('你好') || lowerText.includes('嗨') || lowerText.includes('hi')) {
    return '您好，先生。贾维斯随时待命。请指示。'
  }
  if (lowerText.includes('who are you') || lowerText.includes('你是谁')) {
    return '我是贾维斯，您的个人 AI 助手。我被设计用来协助您管理 OpenClaw 系统，并为您提供各种帮助。'
  }
  if (lowerText.includes('time') || lowerText.includes('时间') || lowerText.includes('几点')) {
    const now = new Date()
    return `先生，现在是 ${now.getHours()}点${now.getMinutes()}分`
  }
  if (lowerText.includes('date') || lowerText.includes('日期') || lowerText.includes('今天')) {
    const now = new Date()
    return `今天是 ${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
  }
  if (lowerText.includes('status') || lowerText.includes('状态') || lowerText.includes('系统状态')) {
    return '先生，所有系统正常运行。反应堆输出 98%，装甲完整，人工智能在线。'
  }
  if (lowerText.includes('thank') || lowerText.includes('谢谢') || lowerText.includes('感谢')) {
    return '为您服务是我的荣幸，先生。'
  }
  if (lowerText.includes('bye') || lowerText.includes('再见') || lowerText.includes('拜拜')) {
    return '先生，祝您有美好的一天。需要我时随时召唤我。'
  }
  if (lowerText.includes('help') || lowerText.includes('帮助') || lowerText.includes('你能做什么')) {
    return `先生，我可以帮助您：
• 查询系统状态和时间
• 执行终端命令
• 管理实例和任务
• 查看告警信息
• 与您进行简单的对话

您可以直接用语音或文字告诉我您的需求。`
  }
  
  return '明白，先生。我会处理这个请求。'
}

// 语音播报
const speak = (text) => {
  if (!synthesis || !voiceEnabled.value) return
  
  // 停止当前正在播放的语音
  synthesis.cancel()
  
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US' // 贾维斯使用英文
  utterance.rate = 0.9 // 语速稍慢，更像贾维斯
  utterance.pitch = 0.8 // 音调稍低
  utterance.volume = 1
  
  utterance.onstart = () => {
    isSpeaking.value = true
  }
  
  utterance.onend = () => {
    isSpeaking.value = false
  }
  
  utterance.onerror = (e) => {
    console.error('语音播放错误:', e)
    isSpeaking.value = false
  }
  
  synthesis.speak(utterance)
}

// 播报当前文本
const speakCurrentText = () => {
  const lastMessage = conversation.value.filter(m => m.role === 'jarvis').pop()
  if (lastMessage) {
    speak(lastMessage.content)
    ElMessage.success('正在语音播报')
  } else {
    ElMessage.warning('没有可播报的内容')
  }
}

// 显示系统信息
const showSystemInfo = () => {
  const info = `先生，系统状态报告：
• 反应堆：98% 正常运行
• 装甲：100% 完整
• 人工智能：100% 在线
• 通信：95% 稳定
• 防御系统：100% 激活
• 能源储备：92% 充足

所有子系统正常运行。`
  
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'jarvis',
    content: info,
    time
  })
  
  if (voiceEnabled.value) {
    speak(info)
  }
}

// 切换语音开关
const toggleVoice = () => {
  voiceEnabled.value = !voiceEnabled.value
  if (voiceEnabled.value) {
    speak('语音功能已启用')
    ElMessage.success('语音功能已启用')
  } else {
    synthesis?.cancel()
    ElMessage.info('语音功能已禁用')
  }
}

// 清空对话
const clearConversation = () => {
  conversation.value = []
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'jarvis',
    content: '对话已清空，先生。',
    time
  })
  
  if (voiceEnabled.value) {
    speak('对话已清空')
  }
}

// 初始化波形可视化
const initWaveform = () => {
  if (!waveformCanvas.value) return
  
  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')
  
  const resize = () => {
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
  }
  
  resize()
  window.addEventListener('resize', resize)
  
  let phase = 0
  
  const draw = () => {
    const width = canvas.width
    const height = canvas.height
    
    ctx.clearRect(0, 0, width, height)
    
    const centerY = height / 2
    const baseAmplitude = isListening.value ? 25 : 8
    const amplitude = isProcessing.value ? baseAmplitude * 1.5 : baseAmplitude
    
    // 绘制多层波形
    for (let layer = 0; layer < 3; layer++) {
      ctx.beginPath()
      const alpha = 0.6 - layer * 0.2
      const lineWidth = 3 - layer
      ctx.strokeStyle = layer === 0 ? `rgba(0, 229, 204, ${alpha})` : `rgba(0, 229, 204, ${alpha * 0.5})`
      ctx.lineWidth = lineWidth
      
      const freq = 0.02 + layer * 0.01
      const phaseOffset = layer * 0.5
      const ampMultiplier = 1 - layer * 0.3
      
      for (let x = 0; x < width; x++) {
        const y = centerY + Math.sin(x * freq + phase + phaseOffset) * amplitude * ampMultiplier
        if (x === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }
      
      ctx.stroke()
    }
    
    // 绘制中心线
    ctx.beginPath()
    ctx.strokeStyle = 'rgba(0, 229, 204, 0.3)'
    ctx.lineWidth = 1
    ctx.moveTo(0, centerY)
    ctx.lineTo(width, centerY)
    ctx.stroke()
    
    phase += 0.05
    animationFrame = requestAnimationFrame(draw)
  }
  
  draw()
}

// 生成随机字符
const randomChar = () => {
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン JarvisJARVIS'
  return chars[Math.floor(Math.random() * chars.length)]
}
</script>

<style scoped>
/* 基础容器 */
.jarvis-container {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(180deg, #050810 0%, #0a1020 30%, #0d1525 60%, #050810 100%);
  overflow: hidden;
  padding: 20px;
  font-family: 'Segoe UI', 'Roboto', sans-serif;
}

/* 全息背景网格 */
.holographic-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(0, 229, 204, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 229, 204, 0.02) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
}

/* 扫描线效果 */
.scanline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    transparent 50%,
    rgba(0, 229, 204, 0.01) 50%
  );
  background-size: 100% 4px;
  pointer-events: none;
  animation: scanline-move 8s linear infinite;
}

@keyframes scanline-move {
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
}

/* 3D 弧形反应堆 */
.arc-reactor {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 150px;
}

.reactor-ring {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
  border: 2px solid rgba(0, 229, 204, 0.4);
  animation: ring-rotate 20s linear infinite;
}

.reactor-ring.outer {
  top: 0;
  width: 280px;
  height: 140px;
  animation-duration: 25s;
}

.reactor-ring.middle {
  top: 20px;
  width: 200px;
  height: 100px;
  border-color: rgba(0, 229, 204, 0.3);
  animation-direction: reverse;
  animation-duration: 18s;
}

.reactor-ring.inner {
  top: 35px;
  width: 130px;
  height: 65px;
  border-color: rgba(0, 229, 204, 0.5);
  animation-duration: 12s;
}

.ring-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(0, 229, 204, 0.3);
}

.reactor-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
}

.core-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 229, 204, 0.8) 0%, rgba(0, 229, 204, 0.2) 50%, transparent 70%);
  animation: core-pulse 2s ease-in-out infinite;
}

.core-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: radial-gradient(circle, #00e5cc 0%, rgba(0, 229, 204, 0.5) 100%);
  box-shadow: 0 0 30px #00e5cc, 0 0 60px rgba(0, 229, 204, 0.5);
}

@keyframes ring-rotate {
  from { transform: translateX(-50%) rotate(0deg); }
  to { transform: translateX(-50%) rotate(360deg); }
}

@keyframes core-pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
}

/* 能量流动画 */
.energy-flow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(0, 229, 204, 0.1) 60deg,
    rgba(0, 229, 204, 0.2) 120deg,
    transparent 180deg,
    transparent 360deg
  );
  animation: energy-rotate 4s linear infinite;
}

@keyframes energy-rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* 全息面板 */
.holographic-panels {
  position: absolute;
  top: 200px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
  pointer-events: none;
}

.holo-panel {
  width: 220px;
  background: rgba(0, 229, 204, 0.03);
  border: 1px solid rgba(0, 229, 204, 0.2);
  border-radius: 8px;
  padding: 15px;
  backdrop-filter: blur(5px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 229, 204, 0.2);
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: #00e5cc;
  letter-spacing: 2px;
}

.panel-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(0, 229, 204, 0.2);
  color: #00e5cc;
}

.panel-status.online {
  animation: status-blink 2s ease-in-out infinite;
}

@keyframes status-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.system-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 11px;
}

.sys-name {
  width: 50px;
  color: rgba(0, 229, 204, 0.7);
}

.sys-bar {
  flex: 1;
  height: 4px;
  background: rgba(0, 229, 204, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.sys-value {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.sys-value-text {
  width: 35px;
  text-align: right;
  color: rgba(0, 229, 204, 0.8);
  font-size: 10px;
}

.time-display {
  text-align: center;
}

.time-main {
  font-size: 32px;
  font-weight: 300;
  color: #00e5cc;
  letter-spacing: 4px;
  text-shadow: 0 0 20px rgba(0, 229, 204, 0.5);
}

.date-display {
  font-size: 14px;
  color: rgba(0, 229, 204, 0.7);
  margin-top: 5px;
}

.weekday {
  font-size: 12px;
  color: rgba(0, 229, 204, 0.5);
  margin-top: 3px;
}

/* 中央核心显示 */
.core-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.core-avatar {
  width: 100px;
  height: 100px;
  animation: avatar-float 3s ease-in-out infinite;
}

@keyframes avatar-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.avatar-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 20px rgba(0, 229, 204, 0.5));
}

.core-status {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00e5cc;
  box-shadow: 0 0 10px #00e5cc;
  animation: status-idle 2s ease-in-out infinite;
}

.status-indicator.active {
  animation: status-active 0.5s ease-in-out infinite;
}

@keyframes status-idle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@keyframes status-active {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.status-text {
  color: #00e5cc;
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* 波形可视化 */
.waveform-section {
  position: absolute;
  bottom: 320px;
  left: 50%;
  transform: translateX(-50%);
  width: 400px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.waveform-canvas {
  width: 100%;
  height: 60px;
}

.waveform-label {
  font-size: 10px;
  color: rgba(0, 229, 204, 0.6);
  letter-spacing: 3px;
  margin-top: 5px;
  animation: label-blink 1s ease-in-out infinite;
}

@keyframes label-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 控制面板 */
.control-panel {
  position: absolute;
  bottom: 200px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 25px;
}

.voice-btn {
  position: relative;
  width: 120px;
  height: 120px;
  border: none;
  background: transparent;
  cursor: pointer;
}

.btn-outer-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid rgba(0, 229, 204, 0.3);
  border-radius: 50%;
  animation: btn-ring-idle 3s ease-in-out infinite;
}

.btn-middle-ring {
  position: absolute;
  top: 15%;
  left: 15%;
  width: 70%;
  height: 70%;
  border: 1px solid rgba(0, 229, 204, 0.2);
  border-radius: 50%;
  animation: btn-ring-idle 2s ease-in-out infinite reverse;
}

@keyframes btn-ring-idle {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.3; }
}

.voice-btn.listening .btn-outer-ring,
.voice-btn.listening .btn-middle-ring {
  animation: btn-ring-active 0.5s ease-in-out infinite;
}

.voice-btn.processing .btn-outer-ring,
.voice-btn.processing .btn-middle-ring {
  animation: btn-ring-active 0.3s ease-in-out infinite;
}

.voice-btn.speaking .btn-outer-ring,
.voice-btn.speaking .btn-middle-ring {
  animation: btn-ring-active 0.6s ease-in-out infinite;
}

@keyframes btn-ring-active {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.4; }
}

.btn-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, rgba(0, 229, 204, 0.2) 0%, rgba(0, 180, 160, 0.2) 100%);
  border: 2px solid #00e5cc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.voice-btn:hover .btn-inner {
  background: linear-gradient(135deg, rgba(0, 229, 204, 0.4) 0%, rgba(0, 180, 160, 0.4) 100%);
  box-shadow: 0 0 40px rgba(0, 229, 204, 0.5);
}

.voice-btn.listening .btn-inner,
.voice-btn.processing .btn-inner,
.voice-btn.speaking .btn-inner {
  background: linear-gradient(135deg, rgba(0, 229, 204, 0.8) 0%, rgba(0, 180, 160, 0.8) 100%);
  box-shadow: 0 0 50px rgba(0, 229, 204, 0.8);
}

.btn-core {
  display: flex;
  align-items: center;
  justify-content: center;
}

.mic-icon {
  width: 30px;
  height: 30px;
  fill: #00e5cc;
}

.voice-waves {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 30px;
}

.voice-waves span {
  width: 4px;
  background: #00e5cc;
  border-radius: 2px;
  animation: voice-wave 0.5s ease-in-out infinite;
}

.voice-waves span:nth-child(1) { height: 15px; animation-delay: 0s; }
.voice-waves span:nth-child(2) { height: 25px; animation-delay: 0.1s; }
.voice-waves span:nth-child(3) { height: 30px; animation-delay: 0.2s; }
.voice-waves span:nth-child(4) { height: 25px; animation-delay: 0.3s; }
.voice-waves span:nth-child(5) { height: 15px; animation-delay: 0.4s; }

@keyframes voice-wave {
  0%, 100% { transform: scaleY(0.4); }
  50% { transform: scaleY(1); }
}

/* 功能按钮 */
.action-buttons {
  display: flex;
  gap: 20px;
}

.action-btn {
  width: 50px;
  height: 50px;
  border: 1px solid rgba(0, 229, 204, 0.4);
  background: rgba(0, 229, 204, 0.05);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn svg {
  width: 22px;
  height: 22px;
  fill: rgba(0, 229, 204, 0.7);
}

.action-btn:hover {
  background: rgba(0, 229, 204, 0.2);
  border-color: #00e5cc;
  box-shadow: 0 0 25px rgba(0, 229, 204, 0.4);
  transform: scale(1.1);
}

.action-btn:hover svg {
  fill: #00e5cc;
}

.action-btn.active {
  background: rgba(0, 229, 204, 0.3);
  border-color: #00e5cc;
}

/* 输入区域 */
.input-area {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 600px;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 8px 8px 8px 20px;
  background: rgba(0, 229, 204, 0.03);
  border: 1px solid rgba(0, 229, 204, 0.3);
  border-radius: 30px;
  position: relative;
  overflow: hidden;
}

.input-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(0, 229, 204, 0.1), transparent);
  animation: input-glow 3s ease-in-out infinite;
}

@keyframes input-glow {
  0%, 100% { transform: translateX(-100%); }
  50% { transform: translateX(100%); }
}

.jarvis-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #00e5cc;
  font-size: 16px;
  padding: 12px 0;
  position: relative;
}

.jarvis-input::placeholder {
  color: rgba(0, 229, 204, 0.4);
}

.send-btn {
  width: 50px;
  height: 50px;
  border: 1px solid rgba(0, 229, 204, 0.5);
  background: rgba(0, 229, 204, 0.15);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
}

.send-btn svg {
  width: 22px;
  height: 22px;
  fill: #00e5cc;
}

.send-btn:hover:not(:disabled) {
  background: rgba(0, 229, 204, 0.4);
  box-shadow: 0 0 25px rgba(0, 229, 204, 0.5);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 对话区域 */
.conversation-area {
  position: absolute;
  top: 380px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 650px;
  height: calc(100vh - 550px);
  overflow-y: auto;
  padding: 20px;
}

.conversation-area::-webkit-scrollbar {
  width: 4px;
}

.conversation-area::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 204, 0.3);
  border-radius: 2px;
}

.message {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  animation: message-fade-in 0.4s ease;
}

@keyframes message-fade-in {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.jarvis-avatar {
  width: 100%;
  height: 100%;
  color: #00e5cc;
  filter: drop-shadow(0 0 5px rgba(0, 229, 204, 0.5));
}

.user-avatar {
  width: 100%;
  height: 100%;
  color: rgba(255, 255, 255, 0.6);
}

.message-content {
  max-width: 75%;
}

.message.jarvis .message-content {
  padding: 15px 20px;
  background: linear-gradient(135deg, rgba(0, 229, 204, 0.1) 0%, rgba(0, 229, 204, 0.05) 100%);
  border: 1px solid rgba(0, 229, 204, 0.2);
  border-radius: 20px 20px 20px 5px;
}

.message.user .message-content {
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px 20px 5px 20px;
}

.message-text {
  color: #e0e0e0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 5px;
}

/* 底部状态栏 */
.status-bar {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 10px 20px;
  background: rgba(0, 229, 204, 0.03);
  border: 1px solid rgba(0, 229, 204, 0.1);
  border-radius: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(0, 229, 204, 0.6);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00e5cc;
}

.status-dot.online {
  box-shadow: 0 0 10px #00e5cc;
  animation: status-blink 2s ease-in-out infinite;
}

.status-label {
  color: rgba(0, 229, 204, 0.4);
}

.status-on {
  color: #00e5cc;
}

.status-off {
  color: rgba(255, 100, 100, 0.6);
}

/* 装饰性数据流 */
.decorative-streams {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.stream-column {
  position: absolute;
  top: 0;
  bottom: 0;
  left: var(--x);
  width: 80px;
  overflow: hidden;
  opacity: 0.15;
}

.stream-content {
  display: flex;
  flex-direction: column;
  animation: stream-move 15s linear infinite;
  animation-delay: var(--delay);
  font-size: 9px;
  color: #00e5cc;
  letter-spacing: 2px;
}

@keyframes stream-move {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}
</style>
