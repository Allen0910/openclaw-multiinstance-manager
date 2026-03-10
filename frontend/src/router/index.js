import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/instances',
    name: 'Instances',
    component: () => import('../views/Instances.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/skills',
    name: 'Skills',
    component: () => import('../views/Skills.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/metrics',
    name: 'Metrics',
    component: () => import('../views/Metrics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-config',
    name: 'AIConfig',
    component: () => import('../views/AIConfig.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/channels',
    name: 'Channels',
    component: () => import('../views/Channels.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/service',
    name: 'Service',
    component: () => import('../views/Service.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/testing',
    name: 'Testing',
    component: () => import('../views/Testing.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/Logs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/jarvis',
    name: 'Jarvis',
    component: () => import('../views/Jarvis.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/commands',
    name: 'Commands',
    component: () => import('../views/Commands.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else {
    next()
  }
})

export default router
