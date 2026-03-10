<template>
  <div class="app-container" :class="{ 'light-theme': isLightTheme }">
    <!-- 登录页面不显示顶部导航和侧边栏 -->
    <template v-if="!isLoginPage">
      <el-header class="header-nav">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            :icon="sidebarToggleIcon"
            @click="toggleSidebar"
            circle
            size="small"
          />
          <div class="logo">
            <svg width="36" height="36" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Lobster Body -->
              <path d="M60 10 C30 10 15 35 15 55 C15 75 30 95 45 100 L45 110 L55 110 L55 100 C55 100 60 102 65 100 L65 110 L75 110 L75 100 C90 95 105 75 105 55 C105 35 90 10 60 10Z" fill="url(#lobster-gradient)" />
              <!-- Left Claw -->
              <path d="M20 45 C5 40 0 50 5 60 C10 70 20 65 25 55 C28 48 25 45 20 45Z" fill="url(#lobster-gradient)" />
              <!-- Right Claw -->
              <path d="M100 45 C115 40 120 50 115 60 C110 70 100 65 95 55 C92 48 95 45 100 45Z" fill="url(#lobster-gradient)" />
              <!-- Antenna -->
              <path d="M45 15 Q35 5 30 8" stroke="#00e5cc" stroke-width="2" stroke-linecap="round" />
              <path d="M75 15 Q85 5 90 8" stroke="#00e5cc" stroke-width="2" stroke-linecap="round" />
              <!-- Eyes -->
              <circle cx="45" cy="35" r="6" fill="#050810" />
              <circle cx="75" cy="35" r="6" fill="#050810" />
              <circle cx="46" cy="34" r="2" fill="#00e5cc" />
              <circle cx="76" cy="34" r="2" fill="#00e5cc" />
              <defs>
                <linearGradient id="lobster-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#FF6B6B" />
                  <stop offset="100%" stop-color="#FF4757" />
                </linearGradient>
              </defs>
            </svg>
            <span class="logo-text">OpenClaw Manage</span>
          </div>
        </div>
        <div class="header-right">
          <div class="header-stats">
            <div class="stat-item">
              <span class="stat-label">在线实例</span>
              <span class="stat-value gradient-text">2</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">告警</span>
              <span class="stat-value warning-text">3</span>
            </div>
          </div>
          <el-button 
            class="theme-toggle" 
            :icon="isLightTheme ? Moon : Sunny" 
            @click="toggleTheme"
            circle
            size="small"
          />
          <el-button type="primary" class="btn-primary logout-btn" @click="logout">
            <el-icon><SwitchButton /></el-icon>
            <span class="btn-text">退出登录</span>
          </el-button>
        </div>
      </el-header>
      <el-container>
        <el-aside
          :width="sidebarWidth"
          class="sidebar"
          :class="{
            collapsed: !isMobile && isCollapsed,
            'mobile-mode': isMobile,
            'mobile-open': isMobile && isMobileMenuOpen
          }"
        >
          <el-menu
            :default-active="$route.path"
            router
            class="sidebar-menu"
            :unique-opened="true"
            :collapse="!isMobile && isCollapsed"
            :collapse-transition="false"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">
              <el-icon class="menu-item-icon"><Monitor /></el-icon>
              <template #title>监控总览</template>
            </el-menu-item>
            <el-menu-item index="/instances">
              <el-icon class="menu-item-icon"><Cpu /></el-icon>
              <template #title>实例管理</template>
            </el-menu-item>
            <el-menu-item index="/tasks">
              <el-icon class="menu-item-icon"><List /></el-icon>
              <template #title>任务中心</template>
            </el-menu-item>
            <el-menu-item index="/alerts">
              <el-icon class="menu-item-icon"><Bell /></el-icon>
              <template #title>告警中心</template>
            </el-menu-item>
            <el-menu-item index="/skills">
              <el-icon class="menu-item-icon"><Box /></el-icon>
              <template #title>技能市场</template>
            </el-menu-item>
            <el-menu-item index="/metrics">
              <el-icon class="menu-item-icon"><DataAnalysis /></el-icon>
              <template #title>性能分析</template>
            </el-menu-item>
            <el-menu-item index="/ai-config">
              <el-icon class="menu-item-icon"><Connection /></el-icon>
              <template #title>AI 配置</template>
            </el-menu-item>
            <el-menu-item index="/channels">
              <el-icon class="menu-item-icon"><Promotion /></el-icon>
              <template #title>消息渠道</template>
            </el-menu-item>
            <el-menu-item index="/service">
              <el-icon class="menu-item-icon"><Operation /></el-icon>
              <template #title>服务管理</template>
            </el-menu-item>
            <el-menu-item index="/logs">
              <el-icon class="menu-item-icon"><Document /></el-icon>
              <template #title>日志查看</template>
            </el-menu-item>
            <el-menu-item index="/testing">
              <el-icon class="menu-item-icon"><VideoCamera /></el-icon>
              <template #title>测试诊断</template>
            </el-menu-item>
            <el-menu-item index="/jarvis">
              <el-icon class="menu-item-icon"><Microphone /></el-icon>
              <template #title>贾维斯</template>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon class="menu-item-icon"><Setting /></el-icon>
              <template #title>系统设置</template>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main-content" :class="{ 'sidebar-collapsed': isCollapsed }">
          <router-view />
        </el-main>
        <div v-if="isMobile && isMobileMenuOpen" class="mobile-sidebar-mask" @click="closeMobileMenu"></div>
      </el-container>
    </template>
    <!-- 登录页面只显示路由内容 -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor, Cpu, List, Bell, Box, Setting, SwitchButton, DataAnalysis, Fold, Expand, Sunny, Moon, Operation, Close, Connection, Promotion, VideoCamera, Document, Microphone } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const isLightTheme = ref(false)
const isMobile = ref(false)
const isMobileMenuOpen = ref(false)
let viewportQuery = null
let viewportQueryHandler = null

// 判断是否为登录页面
const isLoginPage = computed(() => {
  return route.path === '/login'
})

const sidebarToggleIcon = computed(() => {
  if (isMobile.value) {
    return isMobileMenuOpen.value ? Close : Operation
  }
  return isCollapsed.value ? Expand : Fold
})

const sidebarWidth = computed(() => {
  if (isMobile.value) return '220px'
  return isCollapsed.value ? '64px' : '220px'
})

const emitLayoutResize = () => {
  window.dispatchEvent(new Event('resize'))
}

const syncThemeClass = () => {
  const targets = [document.documentElement, document.body]
  targets.forEach((target) => {
    if (!target) return
    target.classList.toggle('light-theme', isLightTheme.value)
  })
}

const syncBodyScroll = () => {
  if (!document?.body) return
  document.body.style.overflow = isMobile.value && isMobileMenuOpen.value ? 'hidden' : ''
}

const closeMobileMenu = () => {
  if (!isMobileMenuOpen.value) return
  isMobileMenuOpen.value = false
}

const handleMenuSelect = () => {
  if (isMobile.value) {
    closeMobileMenu()
  }
}

const syncViewportMode = (matches) => {
  isMobile.value = matches
  if (!matches) {
    isMobileMenuOpen.value = false
  }
}

const toggleSidebar = async () => {
  if (isMobile.value) {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
    syncBodyScroll()
    return
  }

  isCollapsed.value = !isCollapsed.value
  await nextTick()
  emitLayoutResize()
  // 等待侧栏过渡完成后再次触发，确保 ECharts 在折叠/展开后可见
  window.setTimeout(emitLayoutResize, 260)
}

const toggleTheme = () => {
  isLightTheme.value = !isLightTheme.value
  localStorage.setItem('theme', isLightTheme.value ? 'light' : 'dark')
  syncThemeClass()
  emitLayoutResize()
}

const logout = () => {
  localStorage.removeItem('token')
  ElMessage.success('退出登录成功')
  router.push('/login')
}

watch(
  () => route.path,
  async () => {
    if (isMobile.value) {
      closeMobileMenu()
    }
    await nextTick()
    emitLayoutResize()
  }
)

watch([isMobile, isMobileMenuOpen], () => {
  syncBodyScroll()
})

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isLightTheme.value = savedTheme === 'light'
  syncThemeClass()

  viewportQuery = window.matchMedia('(max-width: 720px)')
  syncViewportMode(viewportQuery.matches)
  viewportQueryHandler = (event) => {
    syncViewportMode(event.matches)
    syncBodyScroll()
  }

  if (viewportQuery.addEventListener) {
    viewportQuery.addEventListener('change', viewportQueryHandler)
  } else {
    viewportQuery.addListener(viewportQueryHandler)
  }
})

onBeforeUnmount(() => {
  if (viewportQuery && viewportQueryHandler) {
    if (viewportQuery.removeEventListener) {
      viewportQuery.removeEventListener('change', viewportQueryHandler)
    } else {
      viewportQuery.removeListener(viewportQueryHandler)
    }
  }
  if (document?.body) {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: var(--bg-primary);
  transition: background-color 0.25s ease;
}

.app-container::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 8% 8%, rgba(255, 122, 69, 0.12), transparent 34%),
    radial-gradient(circle at 92% 8%, rgba(53, 210, 192, 0.1), transparent 36%);
  z-index: 0;
}

.header-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 20px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--bg-elevated) 94%, transparent), color-mix(in srgb, var(--bg-secondary) 92%, transparent));
  border-bottom: 1px solid var(--border-color);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  backdrop-filter: blur(12px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.collapse-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  transition: all 0.18s ease;
}

.collapse-btn:hover {
  border-color: color-mix(in srgb, var(--primary-color) 50%, var(--border-color));
  color: var(--text-primary);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.01em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-stats {
  display: flex;
  gap: 18px;
  margin-right: 2px;
  padding: 0 12px;
  border-right: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-value {
  font-size: 14px;
  font-weight: 700;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.warning-text {
  color: var(--warning-color);
}

.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  transition: all 0.18s ease;
}

.theme-toggle:hover {
  border-color: color-mix(in srgb, var(--primary-color) 50%, var(--border-color));
  color: var(--text-primary);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--gradient-primary);
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 500;
}

.logout-btn:hover {
  transform: translateY(-1px);
}

.sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  height: auto;
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-secondary) 96%, transparent), color-mix(in srgb, var(--bg-primary) 96%, transparent));
  border-right: 1px solid var(--border-color);
  transition: width 0.22s ease, transform 0.24s ease, box-shadow 0.24s ease;
  overflow: hidden;
  z-index: 18;
  backdrop-filter: blur(8px);
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-menu {
  border: none;
  height: 100%;
  background: transparent;
  padding: 10px 0;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 5px 10px;
  border-radius: 10px;
  transition: all 0.18s ease;
  color: var(--text-secondary);
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.sidebar-menu :deep(.el-menu-item .menu-item-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, color-mix(in srgb, var(--primary-color) 20%, transparent), color-mix(in srgb, var(--accent-color) 18%, transparent));
  color: var(--text-primary);
}

/* 折叠菜单图标双轴居中，避免激活态出现视觉偏移 */
.sidebar.collapsed .sidebar-menu {
  width: 64px;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu--collapse .el-menu-item),
.sidebar.collapsed .sidebar-menu :deep(.el-menu-item) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  margin: 6px 8px !important;
  min-height: 46px !important;
  line-height: 46px !important;
  border-radius: var(--radius-md) !important;
  text-align: center !important;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item .menu-item-icon),
.sidebar.collapsed .sidebar-menu :deep(.el-menu--collapse .el-menu-item .menu-item-icon) {
  margin: 0 !important;
  width: 20px !important;
  height: 20px !important;
  display: inline-flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: static !important;
  transform: none !important;
  flex: 0 0 20px !important;
  line-height: 1 !important;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item .menu-item-icon svg),
.sidebar.collapsed .sidebar-menu :deep(.el-menu--collapse .el-menu-item .menu-item-icon svg) {
  display: block !important;
  margin: 0 auto !important;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item > .el-tooltip__trigger) {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item > .el-menu-tooltip__trigger) {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, color-mix(in srgb, var(--primary-color) 24%, transparent), color-mix(in srgb, var(--accent-color) 20%, transparent));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent-color) 28%, transparent) inset;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item.is-active)::before {
  display: none;
}

.app-container.light-theme .sidebar-menu :deep(.el-menu-item) {
  color: #364f73;
}

.app-container.light-theme .sidebar-menu :deep(.el-menu-item:hover) {
  background: #e2ecfa;
  color: #192c45;
}

.app-container.light-theme .sidebar-menu :deep(.el-menu-item.is-active) {
  color: #14273f;
  border: 1px solid color-mix(in srgb, var(--accent-color) 25%, var(--border-color));
}

.app-container.light-theme .collapse-btn,
.app-container.light-theme .theme-toggle {
  color: #345175;
  border-color: #b3c7e2;
}

.main-content {
  margin-left: 220px;
  margin-top: 64px;
  min-height: calc(100vh - 64px);
  padding: 18px;
  background: var(--bg-primary);
  transition: margin-left 0.2s ease;
  position: relative;
  z-index: 1;
}

.main-content.sidebar-collapsed {
  margin-left: 64px;
}

.mobile-sidebar-mask {
  position: fixed;
  left: 0;
  right: 0;
  top: 64px;
  bottom: 0;
  background: rgba(6, 12, 24, 0.52);
  backdrop-filter: blur(2px);
  z-index: 30;
}

.app-container.light-theme .mobile-sidebar-mask {
  background: rgba(33, 60, 98, 0.22);
}

@media (max-width: 960px) {
  .header-stats,
  .btn-text {
    display: none;
  }

  .main-content,
  .main-content.sidebar-collapsed {
    margin-left: 64px;
  }
}

@media (max-width: 720px) {
  .sidebar {
    width: 220px !important;
    z-index: 40;
    border-right: 1px solid var(--border-color);
    transform: translateX(calc(-100% - 16px));
    box-shadow: none;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: 0 20px 36px rgba(8, 14, 28, 0.45);
  }

  .sidebar.collapsed {
    width: 220px !important;
  }

  .sidebar-menu,
  .sidebar-menu:not(.el-menu--collapse) {
    width: 220px !important;
  }

  .sidebar.mobile-mode .sidebar-menu :deep(.el-menu-item) {
    margin: 6px 10px;
    border-radius: 10px;
    padding-left: 14px !important;
  }

  .sidebar.mobile-mode .sidebar-menu :deep(.el-menu-item .menu-item-icon) {
    margin-right: 10px;
  }

  .main-content,
  .main-content.sidebar-collapsed {
    margin-left: 0;
    padding: 14px;
  }

  .header-nav {
    padding: 0 12px;
  }

  .logo-text {
    font-size: 15px;
  }
}
</style>
