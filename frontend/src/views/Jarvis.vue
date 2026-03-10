<template>
  <div class="jarvis-container">
    <!-- 背景网格 -->
    <div class="holographic-grid"></div>
    
    <!-- 扫描线 -->
    <div class="scanline-overlay"></div>
    
    <!-- 粒子背景 -->
    <div class="particle-field">
      <canvas ref="particleCanvas"></canvas>
    </div>

    <!-- 顶部系统状态栏 -->
    <div class="system-header">
      <div class="header-left">
        <div class="system-indicator">
          <span class="indicator-dot"></span>
          <span class="indicator-text">JARVIS SYSTEM ONLINE</span>
        </div>
        <div class="system-subtitle">ARTIFICIAL INTELLIGENCE CORE v3.0</div>
      </div>
      <div class="header-center">
        <div class="status-arc">
          <svg viewBox="0 0 200 100" class="arc-svg">
            <defs>
              <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#00D2FF;stop-opacity:0.3" />
                <stop offset="50%" style="stop-color:#00D2FF;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#00D2FF;stop-opacity:0.3" />
              </linearGradient>
            </defs>
            <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="url(#arcGradient)" stroke-width="2"/>
            <circle cx="20" cy="80" r="4" fill="#00D2FF">
              <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="180" cy="80" r="4" fill="#00D2FF">
              <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" begin="1s"/>
            </circle>
          </svg>
          <div class="arc-label">CORE STATUS</div>
        </div>
      </div>
      <div class="header-right">
        <div class="time-display">
          <div class="time-value">{{ currentTime }}</div>
          <div class="time-zone">Asia/Shanghai</div>
        </div>
      </div>
    </div>

    <!-- 左侧系统面板 -->
    <div class="left-panel">
      <div class="panel-frame">
        <div class="panel-corner top-left"></div>
        <div class="panel-corner top-right"></div>
        <div class="panel-corner bottom-left"></div>
        <div class="panel-corner bottom-right"></div>
        
        <div class="panel-title">
          <span class="title-line"></span>
          <span>SYSTEMS</span>
          <span class="title-line"></span>
        </div>
        
        <!-- 环形进度 -->
        <div class="gauge-section">
          <div class="gauge-item" v-for="(gauge, index) in gauges" :key="index">
            <div class="gauge-ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" class="gauge-bg"/>
                <circle 
                  cx="50" cy="50" r="40" 
                  class="gauge-fill"
                  :style="{ 
                    'stroke-dasharray': gauge.value * 2.51 + ' 251',
                    'stroke': gauge.color 
                  }"
                />
              </svg>
              <div class="gauge-value">{{ gauge.value }}%</div>
            </div>
            <div class="gauge-label">{{ gauge.label }}</div>
          </div>
        </div>
        
        <!-- 雷达图 -->
        <div class="radar-section">
          <div class="section-title">RADAR SCAN</div>
          <div class="radar-display">
            <svg viewBox="0 0 200 200" class="radar-svg">
              <circle cx="100" cy="100" r="90" class="radar-ring"/>
              <circle cx="100" cy="100" r="60" class="radar-ring"/>
              <circle cx="100" cy="100" r="30" class="radar-ring"/>
              <line x1="100" y1="10" x2="100" y2="190" class="radar-line"/>
              <line x1="10" y1="100" x2="190" y2="100" class="radar-line"/>
              <polygon 
                :points="radarPoints" 
                class="radar-shape"
                fill="rgba(0, 210, 255, 0.2)"
                stroke="#00D2FF"
                stroke-width="1"
              />
              <circle 
                v-for="(dot, i) in radarDots" 
                :key="i"
                :cx="dot.x" 
                :cy="dot.y" 
                r="2" 
                class="radar-dot"
              />
              <line x1="100" y1="100" :x2="radarLine.x2" :y2="radarLine.y2" class="radar-sweep"/>
            </svg>
          </div>
        </div>
        
        <!-- 实时指标 -->
        <div class="metrics-section">
          <div class="section-title">REAL-TIME METRICS</div>
          <div class="metric-row" v-for="(metric, index) in metrics" :key="index">
            <span class="metric-label">{{ metric.label }}</span>
            <div class="metric-bar">
              <div class="metric-fill" :style="{ width: metric.value + '%', background: metric.color }"></div>
            </div>
            <span class="metric-value">{{ metric.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 中央全息核心 + 语音波纹 -->
    <div class="center-core">
      <!-- 语音波纹效果 -->
      <div class="voice-ripple-container" :class="{ active: isListening || isSpeaking }">
        <div class="ripple ripple-1"></div>
        <div class="ripple ripple-2"></div>
        <div class="ripple ripple-3"></div>
        <div class="ripple ripple-4"></div>
        <div class="ripple ripple-5"></div>
      </div>
      
      <!-- 3D 旋转球体 -->
      <div class="holo-sphere" :class="{ speaking: isSpeaking }">
        <!-- 外环 -->
        <div class="orbit-ring outer">
          <div class="ring-glow"></div>
        </div>
        <!-- 中环 -->
        <div class="orbit-ring middle">
          <div class="ring-glow"></div>
        </div>
        <!-- 内环 -->
        <div class="orbit-ring inner">
          <div class="ring-glow"></div>
        </div>
        
        <!-- 核心球体 -->
        <div class="core-sphere">
          <div class="sphere-wireframe">
            <div class="wire-circle horizontal" v-for="i in 5" :key="'h'+i"></div>
            <div class="wire-circle vertical v1" v-for="i in 3" :key="'v1'+i"></div>
            <div class="wire-circle vertical v2" v-for="i in 3" :key="'v2'+i"></div>
          </div>
          <div class="sphere-glow"></div>
          <div class="sphere-core">
            <div class="core-pulse" :class="{ listening: isListening, speaking: isSpeaking }"></div>
          </div>
        </div>
        
        <!-- 数据粒子 -->
        <div class="data-particles">
          <div 
            class="particle" 
            v-for="i in 30" 
            :key="i"
            :style="getParticleStyle(i)"
          ></div>
        </div>
        
        <!-- 连接线 -->
        <div class="connection-lines">
          <svg viewBox="0 0 400 400" class="lines-svg">
            <circle cx="200" cy="200" r="180" class="connection-circle" fill="none" stroke="rgba(0,210,255,0.1)" stroke-width="1"/>
            <circle cx="200" cy="200" r="140" class="connection-circle" fill="none" stroke="rgba(0,210,255,0.15)" stroke-width="1"/>
            <circle cx="200" cy="200" r="100" class="connection-circle" fill="none" stroke="rgba(0,210,255,0.2)" stroke-width="1"/>
          </svg>
        </div>
      </div>
      
      <!-- 语音波形可视化 -->
      <div class="voice-visualizer" v-if="isListening || isSpeaking">
        <canvas ref="voiceCanvas" class="voice-canvas"></canvas>
      </div>
      
      <!-- 核心标签 -->
      <div class="core-label">
        <span class="label-text">AI CORE</span>
        <span class="label-status" :class="{ listening: isListening, speaking: isSpeaking }">
          {{ statusText }}
        </span>
      </div>
      
      <!-- 语音按钮 -->
      <div class="voice-controls">
        <button 
          class="mic-button"
          :class="{ listening: isListening, processing: isProcessing, speaking: isSpeaking }"
          @mousedown="startListening"
          @mouseup="stopListening"
          @mouseleave="stopListening"
        >
          <div class="mic-outer-ring"></div>
          <div class="mic-inner">
            <svg v-if="!isListening && !isSpeaking" viewBox="0 0 24 24" class="mic-icon">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" fill="currentColor"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" fill="currentColor"/>
            </svg>
            <div v-else class="voice-bars">
              <span v-for="i in 5" :key="i" class="bar"></span>
            </div>
          </div>
        </button>
        <span class="mic-hint">{{ micHint }}</span>
      </div>
    </div>

    <!-- 右侧 AI 助手面板 -->
    <div class="right-panel">
      <div class="panel-frame">
        <div class="panel-corner top-left"></div>
        <div class="panel-corner top-right"></div>
        <div class="panel-corner bottom-left"></div>
        <div class="panel-corner bottom-right"></div>
        
        <div class="panel-title">
          <span class="title-line"></span>
          <span>AI ASSISTANT</span>
          <span class="title-line"></span>
        </div>
        
        <!-- 对话区域 -->
        <div class="chat-section" ref="chatArea">
          <div 
            v-for="(msg, index) in conversation" 
            :key="index"
            class="chat-message"
            :class="msg.role"
          >
            <div class="message-icon">
              <svg v-if="msg.role === 'jarvis'" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1"/>
                <circle cx="12" cy="12" r="4" fill="currentColor"/>
              </svg>
              <svg v-else viewBox="0 0 24 24">
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
        
        <!-- 输入区域 -->
        <div class="input-section">
          <div class="input-wrapper">
            <span class="input-prompt">></span>
            <input 
              v-model="inputText"
              type="text"
              class="command-input"
              placeholder="Enter command..."
              @keyup.enter="sendMessage"
            />
            <button class="send-btn" @click="sendMessage">
              <svg viewBox="0 0 24 24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- 快捷命令 -->
        <div class="quick-commands">
          <button 
            class="cmd-btn" 
            v-for="cmd in quickCommands" 
            :key="cmd"
            @click="executeCommand(cmd)"
          >
            {{ cmd }}
          </button>
        </div>
      </div>
    </div>

    <!-- 底部命令控制台 -->
    <div class="command-console">
      <div class="console-frame">
        <div class="console-header">
          <span class="console-title">COMMAND CONSOLE</span>
          <span class="console-status">
            <span class="status-dot"></span>
            READY
          </span>
        </div>
        <div class="console-input-line">
          <span class="prompt-symbol">▶</span>
          <input 
            v-model="consoleInput"
            type="text"
            class="console-input"
            placeholder="Type command..."
            @keyup.enter="executeConsoleCommand"
          />
        </div>
        <div class="console-output" v-if="consoleOutput">
          <div class="output-line" v-for="(line, i) in consoleOutput" :key="i">{{ line }}</div>
        </div>
      </div>
    </div>

    <!-- 呼吸光晕 -->
    <div class="breath-glow" :class="{ speaking: isSpeaking }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import api from '../utils/axios'

// 状态变量
const inputText = ref('')
const consoleInput = ref('')
const consoleOutput = ref([])
const conversation = ref([])
const chatArea = ref(null)
const particleCanvas = ref(null)
const voiceCanvas = ref(null)

// 语音状态
const isListening = ref(false)
const isProcessing = ref(false)
const isSpeaking = ref(false)
const statusText = ref('ACTIVE')
const micHint = ref('Hold to speak')

// 时间
const currentTime = ref('')

// 环形进度数据
const gauges = ref([
  { label: 'CPU', value: 78, color: '#00D2FF' },
  { label: 'MEMORY', value: 65, color: '#00FF88' },
  { label: 'NETWORK', value: 92, color: '#FF8C00' },
  { label: 'STORAGE', value: 45, color: '#FF4444' },
])

// 实时指标
const metrics = ref([
  { label: 'Requests/sec', value: 1247, color: '#00D2FF' },
  { label: 'Latency', value: 12, color: '#00FF88' },
  { label: 'Uptime', value: 99, color: '#FF8C00' },
  { label: 'Errors', value: 2, color: '#FF4444' },
])

// 雷达图
const radarAngle = ref(0)
const radarDots = ref([
  { x: 150, y: 80 },
  { x: 120, y: 140 },
  { x: 180, y: 120 },
  { x: 160, y: 170 },
  { x: 80, y: 100 },
])

const radarPoints = computed(() => {
  return radarDots.value.map(dot => `${dot.x},${dot.y}`).join(' ')
})

const radarLine = computed(() => {
  const angle = radarAngle.value * Math.PI / 180
  return {
    x2: 100 + 90 * Math.cos(angle),
    y2: 100 + 90 * Math.sin(angle)
  }
})

// 快捷命令
const quickCommands = [
  'analyze system',
  'run diagnostics',
  'activate agents',
  'check status',
  'security scan',
]

let timeInterval = null
let radarInterval = null
let particlesAnimation = null
let voiceAnimation = null
let recognition = null
let synthesis = null

// 粒子样式
const getParticleStyle = (index) => {
  const angle = (index / 30) * 360
  const radius = 120 + Math.random() * 60
  const speed = 20 + Math.random() * 20
  return {
    '--angle': angle + 'deg',
    '--radius': radius + 'px',
    '--speed': speed + 's',
    '--delay': Math.random() * 5 + 's'
  }
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
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
  processResponse(text)
}

// 处理响应
const processResponse = async (text) => {
  isProcessing.value = true
  statusText.value = 'PROCESSING'
  
  try {
    const res = await api.post('/ai/chat', {
      message: text,
      context: conversation.value.slice(-5)
    })
    
    const response = res.data.response || res.data.message || 'Processing request...'
    
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    conversation.value.push({
      role: 'jarvis',
      content: response,
      time
    })
    
    // 语音播报
    speak(response)
  } catch (error) {
    const response = generateResponse(text)
    
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    conversation.value.push({
      role: 'jarvis',
      content: response,
      time
    })
    
    speak(response)
  } finally {
    isProcessing.value = false
    statusText.value = 'ACTIVE'
    scrollToBottom()
  }
}

// 生成本地响应
const generateResponse = (text) => {
  const lower = text.toLowerCase()
  
  if (lower.includes('hello') || lower.includes('你好') || lower.includes('hi')) {
    return 'Greetings. I am JARVIS, your AI assistant.\n\nHow may I serve you?'
  }
  if (lower.includes('status') || lower.includes('状态')) {
    return `SYSTEM STATUS REPORT:\n\n` +
      `• CPU Load: ${gauges.value[0].value}%\n` +
      `• Memory: ${gauges.value[1].value}%\n` +
      `• Network: ${gauges.value[2].value}%\n` +
      `• Storage: ${gauges.value[3].value}%\n\n` +
      `All systems operational.`
  }
  if (lower.includes('help') || lower.includes('帮助')) {
    return `AVAILABLE COMMANDS:\n\n` +
      `• analyze system - Run system analysis\n` +
      `• run diagnostics - Execute diagnostics\n` +
      `• activate agents - Activate AI agents\n` +
      `• check status - View system status\n` +
      `• security scan - Run security scan\n\n` +
      `Or type any message to chat with me.`
  }
  
  return 'Processing your request. Please stand by...'
}

// 使用 Google Translate TTS (免费且稳定)
const speakWithGoogleTTS = (text, lang) => {
  return new Promise((resolve) => {
    try {
      // Google Translate TTS API - 使用正常语速
      const googleTTSUrl = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(text)}&tl=${lang}&client=tw-ob`
      
      const audio = new Audio(googleTTSUrl)
      audio.playbackRate = 1.0 // 正常语速
      
      isSpeaking.value = true
      statusText.value = 'SPEAKING'
      
      // 启动语音可视化
      startVoiceVisualization()
      
      audio.onloadeddata = () => {
        console.log('Audio loaded, duration:', audio.duration)
        audio.play().catch(e => {
          console.log('Play error:', e)
          resolve(false)
        })
      }
      
      audio.onended = () => {
        console.log('Audio ended normally')
        isSpeaking.value = false
        statusText.value = 'ACTIVE'
        stopVoiceVisualization()
        resolve(true)
      }
      
      audio.onerror = (e) => {
        console.log('Audio error:', e)
        isSpeaking.value = false
        statusText.value = 'ACTIVE'
        stopVoiceVisualization()
        // 回退到浏览器 TTS
        resolve(speakWithBrowserTTS(text, lang))
      }
      
      // 超时保护
      setTimeout(() => {
        if (isSpeaking.value) {
          console.log('Audio timeout, stopping')
          audio.pause()
          isSpeaking.value = false
          statusText.value = 'ACTIVE'
          stopVoiceVisualization()
          resolve(true) // 认为播放成功
        }
      }, 30000) // 30秒超时
      
    } catch (e) {
      console.log('Google TTS failed:', e)
      resolve(speakWithBrowserTTS(text, lang))
    }
  })
}

// 浏览器 TTS 回退方案
const speakWithBrowserTTS = (text, lang) => {
  let synth = window.speechSynthesis
  if (!synth) {
    console.warn('Speech synthesis not supported')
    return false
  }
  
  isSpeaking.value = true
  statusText.value = 'SPEAKING'
  
  synth.cancel()
  
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = lang
  utterance.rate = lang === 'zh-CN' ? 1.0 : 0.95
  utterance.pitch = lang === 'zh-CN' ? 1.0 : 0.85 // Jarvis 声音稍低
  utterance.volume = 1.0
  
  // 获取可用的语音
  const voices = synth.getVoices()
  
  if (lang === 'zh-CN') {
    // 选择最好的中文语音
    const chineseVoice = voices.find(v => v.lang.includes('zh-CN') && v.name.includes('Chinese'))
      || voices.find(v => v.lang.includes('zh'))
      || voices.find(v => v.name.includes('Microsoft Huihui'))
    if (chineseVoice) {
      utterance.voice = chineseVoice
    }
  } else {
    // 选择最好的英文语音 - 找更像 Jarvis 的声音
    const englishVoice = voices.find(v => v.lang.includes('en-US') && v.name.includes('Jenna'))
      || voices.find(v => v.lang.includes('en-US') && v.name.includes('Samantha'))
      || voices.find(v => v.lang.includes('en') && v.name.includes('English'))
      || voices.find(v => v.name.includes('Microsoft Zira'))
      || voices.find(v => v.lang.includes('en'))
    if (englishVoice) {
      utterance.voice = englishVoice
    }
  }
  
  utterance.onend = () => {
    isSpeaking.value = false
    statusText.value = 'ACTIVE'
  }
  
  utterance.onerror = (event) => {
    console.error('Speech error:', event)
    isSpeaking.value = false
    statusText.value = 'ACTIVE'
  }
  
  try {
    synth.speak(utterance)
    return true
  } catch (e) {
    console.error('Failed to speak:', e)
    isSpeaking.value = false
    statusText.value = 'ACTIVE'
    return false
  }
}

// 检测文本语言 - 默认中文
const detectLanguage = (text) => {
  // 简单检测：包含中文字符
  const chineseRegex = /[\u4e00-\u9fa5]/
  return chineseRegex.test(text) ? 'zh-CN' : 'zh-CN' // 默认使用中文
}

// 主语音合成函数 - 优先使用 Google TTS
const speak = async (text) => {
  const lang = detectLanguage(text)
  console.log(`JARVIS speaking in ${lang}:`, text.substring(0, 50))
  
  // 优先尝试 Google TTS
  try {
    await speakWithGoogleTTS(text, lang)
  } catch (e) {
    console.log('TTS error, falling back to browser TTS')
    speakWithBrowserTTS(text, lang)
  }
}

// 语音识别
const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) return
  
  recognition = new SpeechRecognition()
  recognition.continuous = false
  recognition.interimResults = true
  recognition.lang = 'zh-CN'
  
  recognition.onstart = () => {
    isListening.value = true
    statusText.value = 'LISTENING'
    micHint.value = 'Listening...'
    startVoiceVisualization()
  }
  
  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join('')
    
    if (event.results[0].isFinal) {
      handleVoiceInput(transcript)
    }
  }
  
  recognition.onerror = () => {
    isListening.value = false
    statusText.value = 'ACTIVE'
    micHint.value = 'Hold to speak'
    stopVoiceVisualization()
  }
  
  recognition.onend = () => {
    isListening.value = false
    if (statusText.value === 'LISTENING') {
      statusText.value = 'ACTIVE'
      micHint.value = 'Hold to speak'
    }
    stopVoiceVisualization()
  }
}

const startListening = () => {
  if (recognition) {
    try {
      recognition.start()
    } catch (e) {
      console.error(e)
    }
  }
}

const stopListening = () => {
  if (recognition && isListening.value) {
    recognition.stop()
  }
}

const handleVoiceInput = (text) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'user',
    content: text,
    time
  })
  
  processResponse(text)
}

// 语音可视化 - 在说话和倾听时都显示
let voiceVisualizationRunning = false

const startVoiceVisualization = () => {
  if (!voiceCanvas.value) return
  if (voiceVisualizationRunning) return // 避免重复启动
  
  voiceVisualizationRunning = true
  const canvas = voiceCanvas.value
  const ctx = canvas.getContext('2d')
  
  canvas.width = 300
  canvas.height = 60
  
  const draw = () => {
    if (!voiceVisualizationRunning) return
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const centerY = canvas.height / 2
    const bars = 30
    const barWidth = canvas.width / bars
    
    for (let i = 0; i < bars; i++) {
      // 说话时显示更强的波动效果
      const height = isSpeaking.value || isListening.value
        ? Math.random() * 40 + 10 
        : Math.sin(Date.now() / 100 + i * 0.5) * 15 + 25
      
      const gradient = ctx.createLinearGradient(0, centerY - height/2, 0, centerY + height/2)
      gradient.addColorStop(0, '#00D2FF')
      gradient.addColorStop(0.5, '#00FF88')
      gradient.addColorStop(1, '#00D2FF')
      
      ctx.fillStyle = gradient
      ctx.fillRect(i * barWidth + 2, centerY - height/2, barWidth - 4, height)
    }
    
    if (voiceVisualizationRunning) {
      requestAnimationFrame(draw)
    }
  }
  
  draw()
}

const stopVoiceVisualization = () => {
  voiceVisualizationRunning = false
  if (voiceCanvas.value) {
    const ctx = voiceCanvas.value.getContext('2d')
    ctx.clearRect(0, 0, voiceCanvas.value.width, voiceCanvas.value.height)
  }
}

// 执行快捷命令
const executeCommand = (cmd) => {
  inputText.value = cmd
  sendMessage()
}

// 控制台命令
const executeConsoleCommand = () => {
  const cmd = consoleInput.value.trim()
  if (!cmd) return
  
  consoleOutput.value = []
  consoleOutput.value.push(`> ${cmd}`)
  
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  
  if (cmd === 'analyze system') {
    consoleOutput.value.push(`[${time}] Initiating system analysis...`)
    setTimeout(() => {
      consoleOutput.value.push(`[${time}] Analysis complete.`)
      consoleOutput.value.push(`CPU: ${gauges.value[0].value}% | Memory: ${gauges.value[1].value}% | Network: ${gauges.value[2].value}%`)
    }, 1000)
  } else if (cmd === 'run diagnostics') {
    consoleOutput.value.push(`[${time}] Running diagnostics...`)
    setTimeout(() => {
      consoleOutput.value.push(`[${time}] Diagnostics passed. No issues found.`)
    }, 1500)
  } else if (cmd === 'activate agents') {
    consoleOutput.value.push(`[${time}] Activating AI agents...`)
    setTimeout(() => {
      consoleOutput.value.push(`[${time}] Agent "闻讯家" activated`)
      consoleOutput.value.push(`[${time}] Agent "金视家" activated`)
      consoleOutput.value.push(`[${time}] Agent "智研家" activated`)
      consoleOutput.value.push(`[${time}] Agent "红策家" activated`)
      consoleOutput.value.push(`[${time}] All agents online.`)
    }, 1000)
  } else {
    consoleOutput.value.push(`[${time}] Command not recognized. Type "help" for available commands.`)
  }
  
  consoleInput.value = ''
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  }, 100)
}

// 初始化粒子
const initParticles = () => {
  if (!particleCanvas.value) return
  
  const canvas = particleCanvas.value
  const ctx = canvas.getContext('2d')
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  resize()
  window.addEventListener('resize', resize)
  
  const particles = []
  const particleCount = 80
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      size: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.3 + 0.05
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(p => {
      p.x += p.vx
      p.y += p.vy
      
      if (p.x < 0) p.x = canvas.width
      if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height
      if (p.y > canvas.height) p.y = 0
      
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(0, 210, 255, ${p.alpha})`
      ctx.fill()
    })
    
    particlesAnimation = requestAnimationFrame(animate)
  }
  
  animate()
}

onMounted(() => {
  updateTime()
  initParticles()
  initSpeechRecognition()
  
  if (window.speechSynthesis) {
    synthesis = window.speechSynthesis
  }
  
  timeInterval = setInterval(() => {
    updateTime()
  }, 1000)
  
  radarInterval = setInterval(() => {
    radarAngle.value = (radarAngle.value + 3) % 360
  }, 50)
  
  // 欢迎消息
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'jarvis',
    content: 'Greetings. I am JARVIS.\n\nI am online and ready to assist you.\n\nHold the microphone button to speak, or type a command.',
    time
  })
})

onBeforeUnmount(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (radarInterval) clearInterval(radarInterval)
  if (particlesAnimation) cancelAnimationFrame(particlesAnimation)
  if (recognition) recognition.stop()
  if (synthesis) synthesis.cancel()
})

watch(conversation, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
/* ========== 基础设置 ========== */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

.jarvis-container {
  position: relative;
  min-height: 100vh;
  background: #000810;
  overflow: hidden;
  font-family: 'Share Tech Mono', 'Orbitron', monospace;
  color: #00D2FF;
}

/* ========== 背景网格 ========== */
.holographic-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(0, 210, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 210, 255, 0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

/* ========== 扫描线 ========== */
.scanline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    transparent 50%,
    rgba(0, 0, 0, 0.03) 50%
  );
  background-size: 100% 4px;
  pointer-events: none;
  animation: scanline-scroll 8s linear infinite;
}

@keyframes scanline-scroll {
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
}

/* ========== 粒子背景 ========== */
.particle-field {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particle-field canvas {
  width: 100%;
  height: 100%;
}

/* ========== 顶部状态栏 ========== */
.system-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  z-index: 100;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.system-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00FF88;
  box-shadow: 0 0 10px #00FF88;
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.indicator-text {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 3px;
  color: #00D2FF;
}

.system-subtitle {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.5);
  letter-spacing: 2px;
}

.header-center {
  display: flex;
  justify-content: center;
}

.status-arc {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.arc-svg {
  width: 150px;
  height: 75px;
}

.arc-label {
  font-size: 9px;
  letter-spacing: 2px;
  color: rgba(0, 210, 255, 0.6);
  margin-top: -10px;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.time-display {
  text-align: right;
}

.time-value {
  font-size: 24px;
  font-weight: 300;
  letter-spacing: 4px;
  color: #00D2FF;
  text-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
}

.time-zone {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.5);
  letter-spacing: 2px;
}

/* ========== 左侧面板 ========== */
.left-panel {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  width: 280px;
  z-index: 50;
}

.panel-frame {
  position: relative;
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.panel-corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 210, 255, 0.6);
}

.top-left { top: -1px; left: -1px; border-right: none; border-bottom: none; border-radius: 8px 0 0 0; }
.top-right { top: -1px; right: -1px; border-left: none; border-bottom: none; border-radius: 0 8px 0 0; }
.bottom-left { bottom: -1px; left: -1px; border-right: none; border-top: none; border-radius: 0 0 0 8px; }
.bottom-right { bottom: -1px; right: -1px; border-left: none; border-top: none; border-radius: 0 0 8px 0; }

.panel-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  font-size: 12px;
  letter-spacing: 3px;
  color: #00D2FF;
}

.title-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 210, 255, 0.5), transparent);
}

/* 环形进度 */
.gauge-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.gauge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge-ring {
  position: relative;
  width: 60px;
  height: 60px;
}

.gauge-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.gauge-bg {
  fill: none;
  stroke: rgba(0, 210, 255, 0.1);
  stroke-width: 6;
}

.gauge-fill {
  fill: none;
  stroke-width: 6;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 11px;
  font-weight: 600;
  color: #00D2FF;
}

.gauge-label {
  font-size: 9px;
  color: rgba(0, 210, 255, 0.6);
  margin-top: 5px;
  letter-spacing: 1px;
}

/* 雷达图 */
.radar-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.6);
  letter-spacing: 2px;
  margin-bottom: 10px;
  text-align: center;
}

.radar-display {
  display: flex;
  justify-content: center;
}

.radar-svg {
  width: 150px;
  height: 150px;
}

.radar-ring {
  fill: none;
  stroke: rgba(0, 210, 255, 0.15);
  stroke-width: 1;
}

.radar-line {
  stroke: rgba(0, 210, 255, 0.1);
  stroke-width: 1;
}

.radar-shape {
  animation: radar-pulse 3s ease-in-out infinite;
}

@keyframes radar-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.radar-dot {
  fill: #00D2FF;
  animation: dot-blink 1.5s ease-in-out infinite;
}

@keyframes dot-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.radar-sweep {
  stroke: rgba(0, 210, 255, 0.3);
  stroke-width: 2;
  animation: sweep-rotate 4s linear infinite;
}

@keyframes sweep-rotate {
  from { transform-origin: 100px 100px; transform: rotate(0deg); }
  to { transform-origin: 100px 100px; transform: rotate(360deg); }
}

/* 实时指标 */
.metrics-section {
  margin-top: 10px;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 9px;
  color: rgba(0, 210, 255, 0.5);
  width: 70px;
}

.metric-bar {
  flex: 1;
  height: 4px;
  background: rgba(0, 210, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.metric-value {
  font-size: 9px;
  color: rgba(0, 210, 255, 0.8);
  width: 30px;
  text-align: right;
}

/* ========== 中央核心 ========== */
.center-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

/* 语音波纹效果 */
.voice-ripple-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.voice-ripple-container.active {
  opacity: 1;
}

.ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(0, 210, 255, 0.6);
  border-radius: 50%;
  animation: ripple-expand 2s ease-out infinite;
}

.ripple-1 { width: 100px; height: 100px; animation-delay: 0s; }
.ripple-2 { width: 130px; height: 130px; animation-delay: 0.3s; }
.ripple-3 { width: 160px; height: 160px; animation-delay: 0.6s; }
.ripple-4 { width: 190px; height: 190px; animation-delay: 0.9s; }
.ripple-5 { width: 220px; height: 220px; animation-delay: 1.2s; }

@keyframes ripple-expand {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}

/* 语音可视化 */
.voice-visualizer {
  position: absolute;
  bottom: -80px;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 60px;
}

.voice-canvas {
  width: 100%;
  height: 100%;
}

.holo-sphere {
  position: relative;
  width: 400px;
  height: 400px;
  transition: transform 0.3s ease;
}

.holo-sphere.speaking {
  animation: sphere-shake 0.1s ease-in-out infinite;
}

@keyframes sphere-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

/* 轨道环 */
.orbit-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(0, 210, 255, 0.3);
}

.orbit-ring.outer {
  width: 380px;
  height: 380px;
  animation: orbit-rotate 30s linear infinite;
}

.orbit-ring.middle {
  width: 280px;
  height: 280px;
  border-color: rgba(255, 140, 0, 0.3);
  animation: orbit-rotate 20s linear infinite reverse;
}

.orbit-ring.inner {
  width: 180px;
  height: 180px;
  animation: orbit-rotate 15s linear infinite;
}

@keyframes orbit-rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.ring-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.2);
}

/* 核心球体 */
.core-sphere {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
}

.sphere-wireframe {
  position: relative;
  width: 100%;
  height: 100%;
}

.wire-circle {
  position: absolute;
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 50%;
}

.wire-circle.horizontal {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.wire-circle.horizontal:nth-child(1) { transform: scaleX(1); }
.wire-circle.horizontal:nth-child(2) { transform: scaleX(0.8); }
.wire-circle.horizontal:nth-child(3) { transform: scaleX(0.6); }
.wire-circle.horizontal:nth-child(4) { transform: scaleX(0.4); }
.wire-circle.horizontal:nth-child(5) { transform: scaleX(0.2); }

.wire-circle.v1 {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  transform: rotate(0deg);
}

.wire-circle.v2 {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  transform: rotate(90deg);
}

.sphere-glow {
  position: absolute;
  top: -20px;
  left: -20px;
  right: -20px;
  bottom: -20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.1) 0%, transparent 70%);
  animation: sphere-glow-pulse 3s ease-in-out infinite;
}

@keyframes sphere-glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.sphere-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
}

.core-pulse {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, #00D2FF 0%, rgba(0, 210, 255, 0.3) 100%);
  box-shadow: 0 0 30px #00D2FF, 0 0 60px rgba(0, 210, 255, 0.5);
  animation: core-heartbeat 2s ease-in-out infinite;
}

.core-pulse.listening {
  animation: core-listening 0.5s ease-in-out infinite;
}

.core-pulse.speaking {
  animation: core-speaking 0.3s ease-in-out infinite;
}

@keyframes core-heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

@keyframes core-listening {
  0%, 100% { transform: scale(1); box-shadow: 0 0 30px #00D2FF; }
  50% { transform: scale(1.3); box-shadow: 0 0 50px #00FF88; }
}

@keyframes core-speaking {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.4); box-shadow: 0 0 60px #FF8C00; }
}

/* 数据粒子 */
.data-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #00D2FF;
  border-radius: 50%;
  box-shadow: 0 0 6px #00D2FF;
  animation: particle-orbit var(--speed) linear infinite;
  animation-delay: var(--delay);
  transform-origin: var(--radius) 0;
  opacity: 0.6;
}

@keyframes particle-orbit {
  from { transform: rotate(var(--angle)) translateX(var(--radius)); }
  to { transform: rotate(calc(var(--angle) + 360deg)) translateX(var(--radius)); }
}

/* 连接线 */
.connection-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.lines-svg {
  width: 100%;
  height: 100%;
  animation: lines-rotate 60s linear infinite;
}

@keyframes lines-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 核心标签 */
.core-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

.label-text {
  font-size: 14px;
  letter-spacing: 4px;
  color: rgba(0, 210, 255, 0.8);
}

.label-status {
  font-size: 10px;
  color: #00FF88;
  letter-spacing: 2px;
  animation: status-blink 1.5s ease-in-out infinite;
}

.label-status.listening {
  color: #00FF88;
  animation: status-listening 0.5s ease-in-out infinite;
}

.label-status.speaking {
  color: #FF8C00;
  animation: status-speaking 0.3s ease-in-out infinite;
}

@keyframes status-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes status-listening {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes status-speaking {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 语音控制按钮 */
.voice-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

.mic-button {
  position: relative;
  width: 80px;
  height: 80px;
  border: none;
  background: transparent;
  cursor: pointer;
}

.mic-outer-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid rgba(0, 210, 255, 0.4);
  border-radius: 50%;
  animation: mic-ring-idle 2s ease-in-out infinite;
  transition: all 0.3s ease;
}

.mic-button.listening .mic-outer-ring,
.mic-button.speaking .mic-outer-ring {
  border-color: rgba(0, 255, 136, 0.8);
  animation: mic-ring-active 0.5s ease-in-out infinite;
}

.mic-button.processing .mic-outer-ring {
  border-color: rgba(255, 140, 0, 0.8);
}

@keyframes mic-ring-idle {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.3; }
}

@keyframes mic-ring-active {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.5; }
}

.mic-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  background: rgba(0, 210, 255, 0.1);
  border: 2px solid rgba(0, 210, 255, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.mic-button:hover .mic-inner {
  background: rgba(0, 210, 255, 0.2);
  border-color: #00D2FF;
}

.mic-button.listening .mic-inner,
.mic-button.speaking .mic-inner {
  background: rgba(0, 255, 136, 0.2);
  border-color: #00FF88;
}

.mic-icon {
  width: 24px;
  height: 24px;
  color: #00D2FF;
}

.voice-bars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 24px;
}

.voice-bars .bar {
  width: 3px;
  background: #00FF88;
  border-radius: 2px;
  animation: voice-bar 0.4s ease-in-out infinite;
}

.voice-bars .bar:nth-child(1) { height: 10px; animation-delay: 0s; }
.voice-bars .bar:nth-child(2) { height: 20px; animation-delay: 0.1s; }
.voice-bars .bar:nth-child(3) { height: 24px; animation-delay: 0.2s; }
.voice-bars .bar:nth-child(4) { height: 16px; animation-delay: 0.3s; }
.voice-bars .bar:nth-child(5) { height: 12px; animation-delay: 0.4s; }

@keyframes voice-bar {
  0%, 100% { transform: scaleY(0.3); }
  50% { transform: scaleY(1); }
}

.mic-hint {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.5);
  margin-top: 10px;
  letter-spacing: 1px;
}

/* ========== 右侧面板 ========== */
.right-panel {
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  width: 320px;
  max-height: 70vh;
  z-index: 50;
}

.right-panel .panel-frame {
  height: 100%;
  max-height: inherit;
  display: flex;
  flex-direction: column;
}

/* 对话区域 */
.chat-section {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  max-height: 300px;
}

.chat-section::-webkit-scrollbar {
  width: 3px;
}

.chat-section::-webkit-scrollbar-thumb {
  background: rgba(0, 210, 255, 0.3);
  border-radius: 2px;
}

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  animation: message-appear 0.3s ease;
}

@keyframes message-appear {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.message-icon svg {
  width: 100%;
  height: 100%;
}

.chat-message.jarvis .message-icon {
  color: #00D2FF;
}

.chat-message.user .message-icon {
  color: rgba(255, 255, 255, 0.5);
}

.message-content {
  max-width: 85%;
}

.chat-message.jarvis .message-content {
  padding: 12px 15px;
  background: rgba(0, 210, 255, 0.05);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: 8px 8px 8px 0;
}

.chat-message.user .message-content {
  padding: 12px 15px;
  background: rgba(255, 140, 0, 0.05);
  border: 1px solid rgba(255, 140, 0, 0.2);
  border-radius: 8px 8px 0 8px;
}

.message-text {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  white-space: pre-wrap;
}

.message-time {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 5px;
}

/* 输入区域 */
.input-section {
  margin-top: 15px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 4px;
}

.input-prompt {
  color: #FF8C00;
  font-size: 14px;
}

.command-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #00D2FF;
  font-family: inherit;
  font-size: 12px;
}

.command-input::placeholder {
  color: rgba(0, 210, 255, 0.3);
}

.send-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(0, 210, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.send-btn svg {
  width: 14px;
  height: 14px;
  color: #00D2FF;
}

.send-btn:hover {
  background: rgba(0, 210, 255, 0.4);
}

/* 快捷命令 */
.quick-commands {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
}

.cmd-btn {
  padding: 5px 10px;
  background: rgba(0, 210, 255, 0.05);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: 4px;
  color: rgba(0, 210, 255, 0.7);
  font-family: inherit;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cmd-btn:hover {
  background: rgba(0, 210, 255, 0.15);
  border-color: rgba(0, 210, 255, 0.5);
  color: #00D2FF;
}

/* ========== 底部命令控制台 ========== */
.command-console {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 50%;
  max-width: 600px;
  z-index: 60;
}

.console-frame {
  background: rgba(0, 10, 20, 0.8);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 6px;
  padding: 15px;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 210, 255, 0.2);
}

.console-title {
  font-size: 11px;
  letter-spacing: 2px;
  color: rgba(0, 210, 255, 0.8);
}

.console-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: #00FF88;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00FF88;
  animation: status-pulse 1.5s ease-in-out infinite;
}

@keyframes status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.console-input-line {
  display: flex;
  align-items: center;
  gap: 10px;
}

.prompt-symbol {
  color: #00D2FF;
  font-size: 14px;
}

.console-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #00D2FF;
  font-family: inherit;
  font-size: 13px;
}

.console-input::placeholder {
  color: rgba(0, 210, 255, 0.3);
}

.console-output {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 210, 255, 0.1);
}

.output-line {
  font-size: 11px;
  color: rgba(0, 210, 255, 0.7);
  margin-bottom: 4px;
}

/* ========== 呼吸光晕 ========== */
.breath-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.03) 0%, transparent 60%);
  pointer-events: none;
  animation: breath-glow 4s ease-in-out infinite;
  z-index: 1;
}

.breath-glow.speaking {
  animation: breath-glow-speaking 1s ease-in-out infinite;
}

@keyframes breath-glow {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
}

@keyframes breath-glow-speaking {
  0%, 100% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.2); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.4); }
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .left-panel, .right-panel {
    width: 240px;
  }
  
  .holo-sphere {
    width: 300px;
    height: 300px;
  }
}

@media (max-width: 900px) {
  .left-panel, .right-panel {
    display: none;
  }
  
  .command-console {
    width: 90%;
  }
}
</style>
