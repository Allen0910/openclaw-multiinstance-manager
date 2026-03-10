<template>
  <div class="jarvis-container">
    <!-- 动态粒子背景 -->
    <div class="particles" ref="particlesContainer">
      <canvas ref="particlesCanvas"></canvas>
    </div>
    
    <!-- 3D 网格背景 -->
    <div class="grid-background">
      <div class="grid-layer layer-1"></div>
      <div class="grid-layer layer-2"></div>
      <div class="grid-layer layer-3"></div>
    </div>
    
    <!-- 顶部状态栏 -->
    <div class="system-header">
      <!-- 左侧：流动日志 -->
      <div class="log-stream-panel">
        <div class="panel-title">
          <span class="title-icon">◈</span>
          SYSTEM LOGS
        </div>
        <div class="log-content" ref="logContent">
          <div class="log-line" v-for="(log, index) in systemLogs" :key="index" :class="log.type">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-text">{{ log.text }}</span>
          </div>
        </div>
      </div>
      
      <!-- 右侧：时间和资源 -->
      <div class="resource-panel">
        <div class="time-display-header">
          <span class="timezone">Asia/Shanghai</span>
          <span class="main-time">{{ currentTime }}</span>
        </div>
        <div class="resource-bars">
          <div class="resource-item">
            <span class="resource-label">CPU</span>
            <div class="resource-bar">
              <div class="resource-fill cpu" :style="{ width: cpuUsage + '%' }"></div>
            </div>
            <span class="resource-value">{{ cpuUsage }}%</span>
          </div>
          <div class="resource-item">
            <span class="resource-label">MEM</span>
            <div class="resource-bar">
              <div class="resource-fill memory" :style="{ width: memoryUsage + '%' }"></div>
            </div>
            <span class="resource-value">{{ memoryUsage }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 中央核心：3D 全息球 -->
    <div class="core-section">
      <div class="holographic-sphere">
        <!-- 外环 -->
        <div class="sphere-ring outer-ring">
          <div class="ring-segment" v-for="i in 12" :key="'o'+i"></div>
        </div>
        <!-- 中环 -->
        <div class="sphere-ring middle-ring">
          <div class="ring-segment" v-for="i in 8" :key="'m'+i"></div>
        </div>
        <!-- 内环 -->
        <div class="sphere-ring inner-ring">
          <div class="ring-segment" v-for="i in 4" :key="'i'+i"></div>
        </div>
        <!-- 核心球体 -->
        <div class="sphere-core">
          <div class="core-pulse-layer"></div>
          <div class="core-inner">
            <div class="core-glow"></div>
          </div>
        </div>
        <!-- 能量粒子 -->
        <div class="energy-particles">
          <div class="particle" v-for="i in 20" :key="'p'+i" :style="getParticleStyle(i)"></div>
        </div>
      </div>
      
      <!-- 四个 Agent 气泡 -->
      <div class="agent-bubbles">
        <div class="agent-bubble" v-for="agent in agents" :key="agent.id" :style="{ '--hue': agent.hue }">
          <div class="bubble-icon">{{ agent.icon }}</div>
          <div class="bubble-name">{{ agent.name }}</div>
          <div class="bubble-status">{{ agent.status }}</div>
        </div>
      </div>
    </div>

    <!-- 左侧面板：GoldSeer -->
    <div class="floating-panel left-panel" ref="leftPanel">
      <div class="panel-scan-line"></div>
      <div class="panel-content">
        <div class="panel-header">
          <span class="panel-badge">◈</span>
          <span class="panel-title">GoldSeer</span>
        </div>
        
        <!-- K线缩略图 -->
        <div class="kline-section">
          <div class="section-label">GOLD K-LINE</div>
          <div class="kline-chart">
            <svg viewBox="0 0 200 60" class="kline-svg">
              <polyline 
                fill="none" 
                stroke="#FF8C00" 
                stroke-width="1.5"
                points="0,45 20,40 40,42 60,35 80,38 100,30 120,32 140,25 160,28 180,20 200,15"
              />
              <polyline 
                fill="none" 
                stroke="rgba(255,140,0,0.3)" 
                stroke-width="8"
                points="0,45 20,40 40,42 60,35 80,38 100,30 120,32 140,25 160,28 180,20 200,15"
              />
            </svg>
            <div class="kline-price">$2,342.80</div>
          </div>
        </div>
        
        <!-- 美元指数 -->
        <div class="dxy-section">
          <div class="section-label">USD INDEX (DXY)</div>
          <div class="dxy-display">
            <span class="dxy-value" :class="{ rising: dxyChange > 0 }">{{ dxyValue }}</span>
            <span class="dxy-change" :class="{ rising: dxyChange > 0 }">
              {{ dxyChange > 0 ? '↑' : '↓' }}{{ Math.abs(dxyChange) }}%
            </span>
          </div>
        </div>
        
        <!-- 避险系数 -->
        <div class="risk-section">
          <div class="section-label">RISK AVOIDANCE</div>
          <div class="risk-bar-container">
            <div class="risk-bar">
              <div class="risk-fill" :style="{ width: riskFactor + '%' }"></div>
            </div>
            <span class="risk-value">{{ riskFactor }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧面板：AIPulse -->
    <div class="floating-panel right-panel" ref="rightPanel">
      <div class="panel-scan-line"></div>
      <div class="panel-content">
        <div class="panel-header">
          <span class="panel-badge">◈</span>
          <span class="panel-title">AIPulse</span>
        </div>
        
        <!-- AI 模型拓扑图 -->
        <div class="topology-section">
          <div class="section-label">NEURAL TOPOLOGY</div>
          <div class="topology-graph">
            <svg viewBox="0 0 160 120" class="topology-svg">
              <!-- 连接线 -->
              <line x1="80" y1="10" x2="40" y2="50" class="topo-line"/>
              <line x1="80" y1="10" x2="120" y2="50" class="topo-line"/>
              <line x1="80" y1="10" x2="80" y2="50" class="topo-line"/>
              <line x1="40" y1="50" x2="20" y2="90" class="topo-line"/>
              <line x1="40" y1="50" x2="60" y2="90" class="topo-line"/>
              <line x1="80" y1="50" x2="80" y2="90" class="topo-line"/>
              <line x1="120" y1="50" x2="100" y2="90" class="topo-line"/>
              <line x1="120" y1="50" x2="140" y2="90" class="topo-line"/>
              <!-- 节点 -->
              <circle cx="80" cy="10" r="6" class="topo-node input"/>
              <circle cx="40" cy="50" r="5" class="topo-node hidden"/>
              <circle cx="80" cy="50" r="5" class="topo-node hidden"/>
              <circle cx="120" cy="50" r="5" class="topo-node hidden"/>
              <circle cx="20" cy="90" r="4" class="topo-node output"/>
              <circle cx="60" cy="90" r="4" class="topo-node output"/>
              <circle cx="80" cy="90" r="4" class="topo-node output"/>
              <circle cx="100" cy="90" r="4" class="topo-node output"/>
              <circle cx="140" cy="90" r="4" class="topo-node output"/>
            </svg>
            <div class="topology-spinner"></div>
          </div>
        </div>
        
        <!-- 技术简报 -->
        <div class="briefing-section">
          <div class="section-label">TECH BRIEFINGS</div>
          <div class="briefing-cards">
            <div class="briefing-card" v-for="(news, index) in techNews" :key="index">
              <span class="briefing-tag">{{ news.tag }}</span>
              <span class="briefing-text">{{ news.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部命令控制台 -->
    <div class="command-console">
      <div class="console-glow"></div>
      <div class="console-input-wrapper">
        <span class="console-prompt"> Jarvis</span>
        <input 
          v-model="inputText" 
          type="text" 
          class="console-input"
          placeholder="输入指令..."
          @keyup.enter="sendMessage"
          @input="onTyping"
        />
        <div class="typing-effects" v-if="isTyping">
          <span class="spark" v-for="i in 5" :key="i"></span>
        </div>
      </div>
    </div>

    <!-- 对话区域 -->
    <div class="conversation-section" ref="conversationArea">
      <div 
        v-for="(msg, index) in conversation" 
        :key="index" 
        class="message"
        :class="msg.role"
      >
        <div class="message-avatar">
          <svg v-if="msg.role === 'jarvis'" viewBox="0 0 24 24" class="jarvis-avatar-icon">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1"/>
            <circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="1"/>
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" class="user-avatar-icon">
            <circle cx="12" cy="8" r="4" fill="currentColor"/>
            <path d="M12 14c-4 0-8 2-8 4v2h16v-2c0-2-4-4-8-4z" fill="currentColor"/>
          </svg>
        </div>
        <div class="message-bubble">
          <div class="message-text">{{ msg.content }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
    </div>

    <!-- 扫描线效果 -->
    <div class="scanline-overlay"></div>
    
    <!-- 呼吸光晕 -->
    <div class="breath-glow"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

// 状态变量
const inputText = ref('')
const isTyping = ref(false)
const conversation = ref([])
const conversationArea = ref(null)
const particlesCanvas = ref(null)
const logContent = ref(null)
const leftPanel = ref(null)
const rightPanel = ref(null)

// 时间
const currentTime = ref('')

// 资源使用率
const cpuUsage = ref(0)
const memoryUsage = ref(0)

// 美元指数
const dxyValue = ref('104.32')
const dxyChange = ref(0.15)

// 避险系数
const riskFactor = ref(72)

// Agent 气泡数据
const agents = ref([
  { id: 1, name: '闻讯家', icon: '📡', status: '在线', hue: 200 },
  { id: 2, name: '金视家', icon: '📊', status: '在线', hue: 35 },
  { id: 3, name: '智研家', icon: '🧠', status: '在线', hue: 280 },
  { id: 4, name: '红策家', icon: '🎯', status: '在线', hue: 160 },
])

// 系统日志
const systemLogs = ref([
  { time: '00:00:01', text: '[BOOT] Jarvis Core initialized', type: 'info' },
  { time: '00:00:02', text: '[LOAD] Neural networks loaded', type: 'success' },
  { time: '00:00:03', text: '[LINK] Connected to GoldSeer', type: 'success' },
  { time: '00:00:04', text: '[LINK] Connected to AIPulse', type: 'success' },
])

// 技术简报
const techNews = ref([
  { tag: 'AI', text: 'GPT-5 发布在即' },
  { tag: '量子', text: '量子计算突破' },
  { tag: '金融', text: 'BTC 突破新高' },
])

let timeInterval = null
let logInterval = null
let resourceInterval = null
let particlesAnimation = null

// 粒子样式
const getParticleStyle = (index) => {
  const angle = (index / 20) * 360
  const distance = 60 + Math.random() * 30
  return {
    '--angle': angle + 'deg',
    '--distance': distance + 'px',
    '--duration': (2 + Math.random() * 2) + 's',
    '--delay': Math.random() * 2 + 's'
  }
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
}

// 更新资源使用率（模拟）
const updateResources = () => {
  cpuUsage.value = Math.floor(30 + Math.random() * 40)
  memoryUsage.value = Math.floor(40 + Math.random() * 35)
}

// 更新日志
const updateLogs = () => {
  const logMessages = [
    '[DATA] Market data synchronized',
    '[AI] Processing query...',
    '[NET] Latency: 12ms',
    '[SYS] Memory optimized',
    '[SEC] Security scan complete',
    '[DATA] Gold prices updated',
    '[AI] Response generated',
  ]
  const types = ['info', 'success', 'warning']
  
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  
  systemLogs.value.push({
    time,
    text: logMessages[Math.floor(Math.random() * logMessages.length)],
    type: types[Math.floor(Math.random() * types.length)]
  })
  
  if (systemLogs.value.length > 8) {
    systemLogs.value.shift()
  }
}

// 打字效果
const onTyping = () => {
  isTyping.value = true
  setTimeout(() => {
    isTyping.value = false
  }, 300)
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

// 处理响应
const processJarvisResponse = async (text) => {
  try {
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
  } catch (error) {
    const localResponse = generateLocalResponse(text)
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    conversation.value.push({
      role: 'jarvis',
      content: localResponse,
      time
    })
  }
  
  scrollToBottom()
}

// 本地响应
const generateLocalResponse = (text) => {
  const lower = text.toLowerCase()
  
  if (lower.includes('hello') || lower.includes('你好')) {
    return '您好，先生。我是贾维斯，为您服务。'
  }
  if (lower.includes('状态') || lower.includes('status')) {
    return '先生，所有系统正常运行。CPU 使用率 ' + cpuUsage.value + '%，内存使用率 ' + memoryUsage.value + '%。'
  }
  if (lower.includes('帮助') || lower.includes('help')) {
    return `先生，我可以帮助您：
• 查询系统状态
• 执行终端命令
• 管理实例和任务
• 查看市场数据（金视家）
• 技术简报（AIPulse）

请直接告诉我您的需求。`
  }
  
  return '明白，先生。我会处理这个请求。'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (conversationArea.value) {
      conversationArea.value.scrollTop = conversationArea.value.scrollHeight
    }
  })
}

// 初始化粒子动画
const initParticles = () => {
  if (!particlesCanvas.value) return
  
  const canvas = particlesCanvas.value
  const ctx = canvas.getContext('2d')
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  resize()
  window.addEventListener('resize', resize)
  
  const particles = []
  const particleCount = 50
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 2 + 1,
      alpha: Math.random() * 0.5 + 0.1
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

// Tilt 效果
const initTiltEffect = (element) => {
  if (!element) return
  
  element.addEventListener('mousemove', (e) => {
    const rect = element.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    
    const rotateX = (y - centerY) / 10
    const rotateY = (centerX - x) / 10
    
    element.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`
  })
  
  element.addEventListener('mouseleave', () => {
    element.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)'
  })
}

onMounted(() => {
  updateTime()
  updateResources()
  initParticles()
  
  timeInterval = setInterval(() => {
    updateTime()
  }, 1000)
  
  resourceInterval = setInterval(() => {
    updateResources()
  }, 3000)
  
  logInterval = setInterval(() => {
    updateLogs()
  }, 2000)
  
  // Tilt 效果
  setTimeout(() => {
    if (leftPanel.value) initTiltEffect(leftPanel.value)
    if (rightPanel.value) initTiltEffect(rightPanel.value)
  }, 100)
  
  // 欢迎消息
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  
  conversation.value.push({
    role: 'jarvis',
    content: '您好，先生。我是贾维斯。\n\n我已连接到四个 AI Agent：\n• 闻讯家 - 实时资讯\n• 金视家 - 市场分析\n• 智研家 - 深度研究\n• 红策家 - 策略建议\n\n请告诉我您需要什么帮助。',
    time
  })
})

onBeforeUnmount(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (logInterval) clearInterval(logInterval)
  if (resourceInterval) clearInterval(resourceInterval)
  if (particlesAnimation) cancelAnimationFrame(particlesAnimation)
})

watch(conversation.value, () => {
  scrollToBottom()
})
</script>

<style scoped>
/* ========== 基础容器 ========== */
.jarvis-container {
  position: relative;
  min-height: 100vh;
  background: #00050A;
  overflow: hidden;
  font-family: 'Orbitron', 'Roboto Mono', 'Consolas', monospace;
  color: #00D2FF;
}

/* ========== 粒子背景 ========== */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particles canvas {
  width: 100%;
  height: 100%;
}

/* ========== 3D 网格背景 ========== */
.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  perspective: 1000px;
  overflow: hidden;
}

.grid-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 200%;
  background-image: 
    linear-gradient(rgba(0, 210, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 210, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.layer-1 {
  transform: rotateX(60deg) translateZ(-100px);
  animation: grid-move-1 20s linear infinite;
  opacity: 0.5;
}

.layer-2 {
  transform: rotateX(60deg) translateZ(0);
  animation: grid-move-2 15s linear infinite;
  opacity: 0.3;
}

.layer-3 {
  transform: rotateX(60deg) translateZ(100px);
  animation: grid-move-3 10s linear infinite;
  opacity: 0.2;
}

@keyframes grid-move-1 {
  0% { transform: rotateX(60deg) translateZ(-100px) translateY(0); }
  100% { transform: rotateX(60deg) translateZ(-100px) translateY(50px); }
}

@keyframes grid-move-2 {
  0% { transform: rotateX(60deg) translateY(0); }
  100% { transform: rotateX(60deg) translateY(50px); }
}

@keyframes grid-move-3 {
  0% { transform: rotateX(60deg) translateZ(100px) translateY(0); }
  100% { transform: rotateX(60deg) translateZ(100px) translateY(50px); }
}

/* ========== 顶部状态栏 ========== */
.system-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  z-index: 100;
}

.log-stream-panel {
  width: 45%;
  background: rgba(0, 210, 255, 0.03);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  backdrop-filter: blur(10px);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #00D2FF;
  margin-bottom: 8px;
}

.title-icon {
  animation: title-pulse 2s ease-in-out infinite;
}

@keyframes title-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.log-content {
  height: 60px;
  overflow: hidden;
  font-size: 10px;
}

.log-line {
  display: flex;
  gap: 10px;
  padding: 2px 0;
  animation: log-fade-in 0.3s ease;
}

@keyframes log-fade-in {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.log-time {
  color: rgba(0, 210, 255, 0.5);
}

.log-text {
  color: rgba(0, 210, 255, 0.8);
}

.log-line.success .log-text { color: #00FF88; }
.log-line.warning .log-text { color: #FF8C00; }
.log-line.error .log-text { color: #FF4444; }

.resource-panel {
  width: 30%;
  background: rgba(0, 210, 255, 0.03);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: 8px;
  padding: 10px 15px;
  backdrop-filter: blur(10px);
}

.time-display-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.timezone {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.5);
  letter-spacing: 1px;
}

.main-time {
  font-size: 20px;
  font-weight: 300;
  letter-spacing: 3px;
  color: #00D2FF;
  text-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
}

.resource-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resource-label {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.6);
  width: 35px;
}

.resource-bar {
  flex: 1;
  height: 6px;
  background: rgba(0, 210, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.resource-fill.cpu {
  background: linear-gradient(90deg, #00D2FF, #00FF88);
}

.resource-fill.memory {
  background: linear-gradient(90deg, #FF8C00, #FFDD00);
}

.resource-value {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.8);
  width: 40px;
  text-align: right;
}

/* ========== 中央核心 ========== */
.core-section {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.holographic-sphere {
  position: relative;
  width: 300px;
  height: 300px;
}

.sphere-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(0, 210, 255, 0.3);
}

.outer-ring {
  width: 280px;
  height: 280px;
  animation: ring-rotate-outer 25s linear infinite;
}

.middle-ring {
  width: 200px;
  height: 200px;
  border-color: rgba(255, 140, 0, 0.3);
  animation: ring-rotate-middle 18s linear infinite reverse;
}

.inner-ring {
  width: 120px;
  height: 120px;
  border-color: rgba(0, 210, 255, 0.5);
  animation: ring-rotate-inner 12s linear infinite;
}

@keyframes ring-rotate-outer {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes ring-rotate-middle {
  from { transform: translate(-50%, -50%) rotate(360deg); }
  to { transform: translate(-50%, -50%) rotate(0deg); }
}

@keyframes ring-rotate-inner {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.ring-segment {
  position: absolute;
  width: 10px;
  height: 10px;
  background: rgba(0, 210, 255, 0.6);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0, 210, 255, 0.8);
}

.outer-ring .ring-segment {
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
}

.middle-ring .ring-segment {
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 140, 0, 0.6);
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.8);
}

.inner-ring .ring-segment {
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
}

.sphere-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
}

.core-pulse-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.4) 0%, transparent 70%);
  animation: core-heartbeat 2s ease-in-out infinite;
}

@keyframes core-heartbeat {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.5); opacity: 0.4; }
}

.core-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: radial-gradient(circle, #00D2FF 0%, rgba(0, 210, 255, 0.5) 100%);
  box-shadow: 0 0 30px #00D2FF, 0 0 60px rgba(0, 210, 255, 0.5);
}

.core-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.3) 0%, transparent 70%);
  animation: core-glow-pulse 1.5s ease-in-out infinite;
}

@keyframes core-glow-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 能量粒子 */
.energy-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #00D2FF;
  border-radius: 50%;
  box-shadow: 0 0 6px #00D2FF;
  animation: particle-orbit var(--duration) linear infinite;
  animation-delay: var(--delay);
  transform-origin: var(--distance) 0;
  opacity: 0.8;
}

@keyframes particle-orbit {
  from { transform: rotate(var(--angle)) translateX(var(--distance)); }
  to { transform: rotate(calc(var(--angle) + 360deg)) translateX(var(--distance)); }
}

/* Agent 气泡 */
.agent-bubbles {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.agent-bubble {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid hsla(var(--hue), 80%, 60%, 0.3);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  animation: bubble-float 3s ease-in-out infinite;
  transition: all 0.3s ease;
}

.agent-bubble:hover {
  transform: translateY(-10px);
  border-color: hsla(var(--hue), 80%, 60%, 0.8);
  box-shadow: 0 10px 30px hsla(var(--hue), 80%, 60%, 0.3);
}

@keyframes bubble-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.bubble-icon {
  font-size: 24px;
}

.bubble-name {
  font-size: 11px;
  color: hsla(var(--hue), 80%, 70%, 1);
  letter-spacing: 1px;
}

.bubble-status {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
}

/* ========== 浮动面板 ========== */
.floating-panel {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 260px;
  background: rgba(0, 10, 20, 0.7);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(20px);
  overflow: hidden;
  transition: transform 0.3s ease;
  z-index: 20;
}

.left-panel {
  left: 30px;
}

.right-panel {
  right: 30px;
}

.panel-scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00D2FF, transparent);
  animation: scan-line 3s linear infinite;
}

@keyframes scan-line {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.panel-content {
  padding: 15px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 210, 255, 0.2);
}

.panel-badge {
  color: #FF8C00;
  animation: badge-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2px;
}

.section-label {
  font-size: 10px;
  color: rgba(0, 210, 255, 0.6);
  letter-spacing: 2px;
  margin-bottom: 8px;
}

/* K线图 */
.kline-section {
  margin-bottom: 15px;
}

.kline-chart {
  position: relative;
  height: 60px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 5px;
}

.kline-svg {
  width: 100%;
  height: 100%;
}

.kline-price {
  position: absolute;
  bottom: 8px;
  right: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #FF8C00;
}

/* 美元指数 */
.dxy-section {
  margin-bottom: 15px;
}

.dxy-display {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.dxy-value {
  font-size: 28px;
  font-weight: 300;
  color: #00D2FF;
}

.dxy-change {
  font-size: 12px;
  color: #00FF88;
}

.dxy-change.rising {
  color: #00FF88;
}

/* 避险系数 */
.risk-section {
  margin-bottom: 10px;
}

.risk-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 210, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.risk-fill {
  height: 100%;
  background: linear-gradient(90deg, #00D2FF, #FF8C00);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.risk-value {
  font-size: 12px;
  color: #FF8C00;
}

/* 拓扑图 */
.topology-section {
  margin-bottom: 15px;
}

.topology-graph {
  position: relative;
  height: 120px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
}

.topology-svg {
  width: 100%;
  height: 100%;
}

.topo-line {
  stroke: rgba(0, 210, 255, 0.3);
  stroke-width: 1;
}

.topo-node {
  fill: rgba(0, 210, 255, 0.8);
}

.topo-node.input {
  fill: #00D2FF;
}

.topo-node.hidden {
  fill: rgba(0, 210, 255, 0.6);
}

.topo-node.output {
  fill: #FF8C00;
}

.topology-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: 2px solid transparent;
  border-top-color: rgba(0, 210, 255, 0.5);
  border-radius: 50%;
  animation: spinner-rotate 2s linear infinite;
}

@keyframes spinner-rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* 技术简报 */
.briefing-section {
  margin-bottom: 10px;
}

.briefing-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.briefing-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 11px;
}

.briefing-tag {
  padding: 2px 6px;
  background: rgba(255, 140, 0, 0.2);
  color: #FF8C00;
  border-radius: 4px;
  font-size: 9px;
}

.briefing-text {
  color: rgba(255, 255, 255, 0.7);
}

/* ========== 底部命令控制台 ========== */
.command-console {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  max-width: 600px;
  z-index: 30;
}

.console-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(0, 210, 255, 0.1), transparent);
  animation: console-glow 3s ease-in-out infinite;
  border-radius: 30px;
}

@keyframes console-glow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.console-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(0, 10, 20, 0.8);
  border: 1px solid rgba(0, 210, 255, 0.3);
  border-radius: 30px;
  position: relative;
  overflow: visible;
}

.console-prompt {
  color: #FF8C00;
  font-weight: 600;
}

.console-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #00D2FF;
  font-family: inherit;
  font-size: 14px;
}

.console-input::placeholder {
  color: rgba(0, 210, 255, 0.3);
}

/* 打字火花效果 */
.typing-effects {
  position: absolute;
  right: 60px;
  display: flex;
  gap: 3px;
}

.spark {
  width: 3px;
  height: 3px;
  background: #FF8C00;
  border-radius: 50%;
  animation: spark-fly 0.3s ease-out;
}

.spark:nth-child(1) { animation-delay: 0s; }
.spark:nth-child(2) { animation-delay: 0.05s; }
.spark:nth-child(3) { animation-delay: 0.1s; }
.spark:nth-child(4) { animation-delay: 0.15s; }
.spark:nth-child(5) { animation-delay: 0.2s; }

@keyframes spark-fly {
  0% { transform: translateY(0) scale(1); opacity: 1; }
  100% { transform: translateY(-10px) scale(0); opacity: 0; }
}

/* ========== 对话区域 ========== */
.conversation-section {
  position: absolute;
  bottom: 160px;
  left: 50%;
  transform: translateX(-50%);
  width: 50%;
  max-width: 500px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  z-index: 25;
}

.conversation-section::-webkit-scrollbar {
  width: 3px;
}

.conversation-section::-webkit-scrollbar-thumb {
  background: rgba(0, 210, 255, 0.3);
  border-radius: 2px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  animation: message-appear 0.3s ease;
}

@keyframes message-appear {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
}

.jarvis-avatar-icon, .user-avatar-icon {
  width: 100%;
  height: 100%;
}

.jarvis-avatar-icon {
  color: #00D2FF;
  filter: drop-shadow(0 0 5px rgba(0, 210, 255, 0.5));
}

.user-avatar-icon {
  color: rgba(255, 255, 255, 0.5);
}

.message-bubble {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 15px;
}

.message.jarvis .message-bubble {
  background: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.3);
}

.message.user .message-bubble {
  background: rgba(255, 140, 0, 0.1);
  border: 1px solid rgba(255, 140, 0, 0.3);
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
  margin-top: 4px;
}

/* ========== 扫描线效果 ========== */
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
  animation: scanline-scroll 10s linear infinite;
}

@keyframes scanline-scroll {
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
}

/* ========== 呼吸光晕 ========== */
.breath-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 210, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
  animation: breath-glow-anim 4s ease-in-out infinite;
  z-index: 1;
}

@keyframes breath-glow-anim {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .left-panel, .right-panel {
    width: 220px;
  }
  
  .agent-bubbles {
    gap: 10px;
  }
  
  .agent-bubble {
    padding: 8px 10px;
  }
}

@media (max-width: 768px) {
  .system-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .log-stream-panel, .resource-panel {
    width: 100%;
  }
  
  .floating-panel {
    display: none;
  }
  
  .command-console {
    width: 90%;
  }
  
  .conversation-section {
    width: 90%;
  }
}
</style>
