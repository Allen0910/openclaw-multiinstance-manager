<template>
  <div class="login-container">
    <div class="login-bg">
      <div class="particles">
        <div class="particle" v-for="i in 30" :key="i" :style="getParticleStyle(i)"></div>
      </div>
      <div class="bg-grid"></div>
    </div>
    
      <div class="login-card card-glow">
        <div class="login-header">
          <div class="logo-large">
            <svg width="64" height="64" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Lobster Body -->
              <path d="M60 10 C30 10 15 35 15 55 C15 75 30 95 45 100 L45 110 L55 110 L55 100 C55 100 60 102 65 100 L65 110 L75 110 L75 100 C90 95 105 75 105 55 C105 35 90 10 60 10Z" fill="url(#lobster-gradient-login)" />
              <!-- Left Claw -->
              <path d="M20 45 C5 40 0 50 5 60 C10 70 20 65 25 55 C28 48 25 45 20 45Z" fill="url(#lobster-gradient-login)" />
              <!-- Right Claw -->
              <path d="M100 45 C115 40 120 50 115 60 C110 70 100 65 95 55 C92 48 95 45 100 45Z" fill="url(#lobster-gradient-login)" />
              <!-- Antenna -->
              <path d="M45 15 Q35 5 30 8" stroke="#00e5cc" stroke-width="2" stroke-linecap="round" />
              <path d="M75 15 Q85 5 90 8" stroke="#00e5cc" stroke-width="2" stroke-linecap="round" />
              <!-- Eyes -->
              <circle cx="45" cy="35" r="6" fill="#050810" />
              <circle cx="75" cy="35" r="6" fill="#050810" />
              <circle cx="46" cy="34" r="2" fill="#00e5cc" />
              <circle cx="76" cy="34" r="2" fill="#00e5cc" />
              <defs>
                <linearGradient id="lobster-gradient-login" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#FF6B6B" />
                  <stop offset="100%" stop-color="#FF4757" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="login-title">OpenClaw Manager</h1>
          <p class="login-subtitle">多实例统一管理平台</p>
        </div>
      
      <el-form :model="form" class="login-form" @submit.prevent="login">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            size="large"
            prefix-icon="User"
            class="input-custom"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
            size="large"
            prefix-icon="Lock"
            @keyup.enter="login"
            class="input-custom"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="login-btn btn-primary pulse" 
            @click="login" 
            :loading="loading"
          >
            {{ loading ? '登录中...' : '进入系统' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p style="font-size: 12px; color: var(--text-muted); text-align: center">
          © 2026 OpenClaw. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import api from '../utils/axios'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'admin123'
})

const getParticleStyle = (i) => {
  const size = Math.random() * 4 + 1
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 5}s`,
    animationDuration: `${Math.random() * 10 + 10}s`
  }
}

const login = async () => {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)
    
    const res = await api.post('/token', formData)
    localStorage.setItem('token', res.data.access_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-primary);
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.bg-grid {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.1;
}

.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  background: var(--primary-color);
  border-radius: 50%;
  opacity: 0.3;
  animation: float linear infinite;
  filter: blur(1px);
}

@keyframes float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

.login-card {
  width: min(420px, 92vw);
  padding: 40px;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(20px);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-large {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 20px rgba(255, 107, 107, 0.5));
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF4757 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.login-form {
  margin-bottom: 30px;
}

.input-custom :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  height: 48px;
  transition: all 0.3s ease;
}

.input-custom :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
}

.input-custom :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF4757 100%);
  border: none;
}

.login-btn:hover {
  background: linear-gradient(135deg, #FF4757 0%, #FF6B6B 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

@media (max-width: 640px) {
  .login-card {
    padding: 24px 20px;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>
