<template>
  <div class="settings-page">
    <h2 class="page-title">系统设置</h2>
    
    <!-- 系统信息 -->
    <div class="card-glow" style="margin-bottom: 20px">
      <div class="section-header">
        <h3><el-icon><InfoFilled /></el-icon> 系统信息</h3>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">系统版本</span>
          <span class="info-value">v1.0.0</span>
        </div>
        <div class="info-item">
          <span class="info-label">部署时间</span>
          <span class="info-value">2026-03-08</span>
        </div>
        <div class="info-item">
          <span class="info-label">实例数量</span>
          <span class="info-value">{{ instanceCount }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">运行时长</span>
          <span class="info-value">7天12小时</span>
        </div>
      </div>
    </div>

    <!-- 告警配置 -->
    <div class="card-glow" style="margin-bottom: 20px">
      <div class="section-header">
        <h3><el-icon><Bell /></el-icon> 告警配置</h3>
      </div>
      <div class="form-container">
        <el-form :model="alertConfig" label-width="150px" class="form-custom">
          <el-form-item label="CPU使用率告警阈值">
            <div class="slider-container">
              <el-slider v-model="alertConfig.cpu_threshold" :min="0" :max="100" :format-tooltip="val => `${val}%`" />
              <span class="slider-value">{{ alertConfig.cpu_threshold }}%</span>
            </div>
          </el-form-item>
          <el-form-item label="内存使用率告警阈值">
            <div class="slider-container">
              <el-slider v-model="alertConfig.memory_threshold" :min="0" :max="100" :format-tooltip="val => `${val}%`" />
              <span class="slider-value">{{ alertConfig.memory_threshold }}%</span>
            </div>
          </el-form-item>
          <el-form-item label="磁盘使用率告警阈值">
            <div class="slider-container">
              <el-slider v-model="alertConfig.disk_threshold" :min="0" :max="100" :format-tooltip="val => `${val}%`" />
              <span class="slider-value">{{ alertConfig.disk_threshold }}%</span>
            </div>
          </el-form-item>
          <el-form-item label="离线告警超时时间">
            <div class="slider-container">
              <el-input-number v-model="alertConfig.offline_timeout" :min="1" :max="300" />
              <span class="slider-value">秒</span>
            </div>
          </el-form-item>
          <el-form-item label="告警通知方式">
            <el-checkbox-group v-model="alertConfig.notify_types">
              <el-checkbox label="feishu">飞书通知</el-checkbox>
              <el-checkbox label="email">邮件通知</el-checkbox>
              <el-checkbox label="sms">短信通知</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="btn-primary" @click="saveAlertConfig">保存配置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 用户管理 -->
    <div class="card-glow">
      <div class="section-header">
        <h3><el-icon><User /></el-icon> 用户管理</h3>
        <el-button type="primary" class="btn-primary" size="small" @click="addUserDialogVisible = true">
          <el-icon><Plus /></el-icon>
          添加用户
        </el-button>
      </div>
      <div class="table-custom">
        <el-table :data="users" border stripe style="width: 100%">
          <el-table-column prop="username" label="用户名" min-width="160" />
          <el-table-column prop="email" label="邮箱" min-width="220" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'primary'" size="small">
                {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'info'" class="tag-success" size="small">
                {{ scope.row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-button size="small" type="warning" link @click="editUser(scope.row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" link @click="deleteUser(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 添加用户对话框 -->
    <el-dialog v-model="addUserDialogVisible" title="添加用户" width="500px" class="dialog-custom">
      <el-form :model="userForm" label-width="80px" class="form-custom">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addUserDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="saveUser" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editUserDialogVisible" title="编辑用户" width="500px" class="dialog-custom">
      <el-form :model="editUserForm" label-width="80px" class="form-custom">
        <el-form-item label="用户名">
          <el-input v-model="editUserForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="editUserForm.password" type="password" show-password placeholder="留空则不修改密码" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editUserForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editUserForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editUserForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editUserDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="updateUser" :loading="updating">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/axios'

const instanceCount = ref(0)
const addUserDialogVisible = ref(false)
const editUserDialogVisible = ref(false)
const saving = ref(false)
const updating = ref(false)
const editingUserId = ref(null)
const users = ref([])
const alertConfig = reactive({
  cpu_threshold: 90,
  memory_threshold: 90,
  disk_threshold: 90,
  offline_timeout: 180,
  notify_types: ['feishu']
})
const userForm = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user'
})
const editUserForm = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user',
  is_active: true
})

const fetchSystemInfo = async () => {
  try {
    const res = await api.get('/instances/')
    instanceCount.value = res.data.length
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const fetchUsers = async () => {
  try {
    const res = await api.get('/users/')
    users.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const saveAlertConfig = () => {
  localStorage.setItem('openclaw_alert_config', JSON.stringify(alertConfig))
  ElMessage.success('告警配置保存成功')
}

const saveUser = async () => {
  saving.value = true
  try {
    await api.post('/users/', userForm)
    ElMessage.success('用户添加成功')
    addUserDialogVisible.value = false
    fetchUsers()
    // 重置表单
    Object.assign(userForm, {
      username: '',
      password: '',
      email: '',
      role: 'user'
    })
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    saving.value = false
  }
}

const editUser = (row) => {
  editingUserId.value = row.id
  Object.assign(editUserForm, {
    username: row.username || '',
    password: '',
    email: row.email || '',
    role: row.role || 'user',
    is_active: row.is_active !== false
  })
  editUserDialogVisible.value = true
}

const updateUser = async () => {
  if (!editingUserId.value) return
  if (!editUserForm.username) {
    ElMessage.warning('用户名不能为空')
    return
  }

  const payload = {
    username: editUserForm.username,
    email: editUserForm.email,
    role: editUserForm.role,
    is_active: editUserForm.is_active
  }
  if (editUserForm.password) {
    payload.password = editUserForm.password
  }

  updating.value = true
  try {
    await api.put(`/users/${editingUserId.value}`, payload)
    ElMessage.success('用户更新成功')
    editUserDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    updating.value = false
  }
}

const deleteUser = async (row) => {
  if (row.username === 'admin') {
    ElMessage.error('管理员账号不能删除')
    return
  }
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/users/${row.id}`)
    ElMessage.success('删除成功')
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已在 axios 拦截器中处理
    }
  }
}

onMounted(() => {
  const saved = localStorage.getItem('openclaw_alert_config')
  if (saved) {
    try {
      Object.assign(alertConfig, JSON.parse(saved))
    } catch (error) {
      // ignore invalid local cache
    }
  }
  fetchSystemInfo()
  fetchUsers()
})
</script>

<style scoped>
.settings-page {
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 0 20px 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 13px;
  color: var(--text-muted);
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-container {
  padding: 0 20px 20px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.slider-container .el-slider {
  flex: 1;
}

.slider-value {
  min-width: 45px;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.action-buttons .el-button {
  padding: 4px 6px;
  margin-left: 0;
}

@media (max-width: 960px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .section-header {
    padding: 16px 16px 0;
  }

  .form-container,
  .info-grid {
    padding-left: 16px;
    padding-right: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .slider-container {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
}
</style>
