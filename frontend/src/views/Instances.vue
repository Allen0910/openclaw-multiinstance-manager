<template>
  <div class="instances-page">
    <div class="page-header">
      <h2>实例管理</h2>
      <el-button type="primary" class="btn-primary" @click="addInstanceDialogVisible = true">
        <el-icon><Plus /></el-icon>
        添加实例
      </el-button>
    </div>

    <div class="card-glow">
      <div class="table-custom">
        <el-table :data="instances" border stripe style="width: 100%">
          <el-table-column prop="name" label="实例名称" min-width="160">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <span class="status-dot" :class="scope.row.status === 'online' ? 'status-online' : 'status-offline'"></span>
                <span style="margin-left: 8px">{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="host" label="主机地址" min-width="160" />
          <el-table-column prop="port" label="端口" width="100" />
          <el-table-column prop="group" label="分组" min-width="130" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'online' ? 'success' : 'danger'" class="tag-success" size="small">
                {{ scope.row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="版本" width="110" />
          <el-table-column prop="cpu_usage" label="CPU使用率" width="180">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <div class="progress-custom" style="flex: 1; margin-right: 10px">
                  <div 
                    class="progress-custom-bar" 
                    :class="getProgressClass(scope.row.cpu_usage)"
                    :style="{ width: `${Math.round(scope.row.cpu_usage)}%` }"
                  ></div>
                </div>
                <span style="min-width: 50px; text-align: right">{{ scope.row.cpu_usage.toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="memory_usage" label="内存使用率" width="180">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <div class="progress-custom" style="flex: 1; margin-right: 10px">
                  <div 
                    class="progress-custom-bar" 
                    :class="getProgressClass(scope.row.memory_usage)"
                    :style="{ width: `${Math.round(scope.row.memory_usage)}%` }"
                  ></div>
                </div>
                <span style="min-width: 50px; text-align: right">{{ scope.row.memory_usage.toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="last_heartbeat" label="最后心跳" min-width="190" />
          <el-table-column label="操作" width="230" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-button size="small" type="primary" link @click="viewInstance(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button size="small" type="warning" link @click="editInstance(scope.row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" link @click="deleteInstance(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 添加实例对话框 -->
    <el-dialog v-model="addInstanceDialogVisible" title="添加实例" width="500px" class="dialog-custom">
      <el-form :model="instanceForm" label-width="80px" class="form-custom">
        <el-form-item label="实例名称" prop="name">
          <el-input v-model="instanceForm.name" placeholder="请输入实例名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="instanceForm.host" placeholder="请输入主机IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="instanceForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="instanceForm.api_key" type="password" placeholder="请输入API密钥" />
        </el-form-item>
        <el-form-item label="分组" prop="group">
          <el-input v-model="instanceForm.group" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="instanceForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addInstanceDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="saveInstance" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editInstanceDialogVisible" title="编辑实例" width="500px" class="dialog-custom">
      <el-form :model="editForm" label-width="80px" class="form-custom">
        <el-form-item label="实例名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入实例名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="editForm.host" placeholder="请输入主机IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="editForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="editForm.api_key" type="password" show-password placeholder="请输入API密钥（留空不修改）" />
        </el-form-item>
        <el-form-item label="分组" prop="group">
          <el-input v-model="editForm.group" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editInstanceDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="updateInstance" :loading="updating">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="instanceDetailVisible" title="实例详情" width="820px" class="dialog-custom">
      <div v-loading="detailLoading" class="instance-detail">
        <el-descriptions v-if="detail.instance" :column="2" border>
          <el-descriptions-item label="实例名称">{{ detail.instance.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detail.instance.status }}</el-descriptions-item>
          <el-descriptions-item label="主机地址">{{ detail.instance.host }}:{{ detail.instance.port }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ detail.instance.version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="CPU">{{ Number(detail.instance.cpu_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="内存">{{ Number(detail.instance.memory_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="磁盘">{{ Number(detail.instance.disk_usage || 0).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="最后心跳">{{ detail.instance.last_heartbeat || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>最近任务</h4>
          <el-table :data="detail.tasks" border stripe style="width: 100%">
            <el-table-column prop="name" label="任务名称" min-width="180" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="created_at" label="创建时间" min-width="180" />
          </el-table>
        </div>

        <div class="detail-section">
          <h4>最近监控点</h4>
          <el-table :data="detail.metrics" border stripe style="width: 100%">
            <el-table-column prop="created_at" label="时间" min-width="180" />
            <el-table-column prop="cpu_usage" label="CPU" width="100">
              <template #default="scope">{{ Number(scope.row.cpu_usage || 0).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="memory_usage" label="内存" width="100">
              <template #default="scope">{{ Number(scope.row.memory_usage || 0).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="disk_usage" label="磁盘" width="100">
              <template #default="scope">{{ Number(scope.row.disk_usage || 0).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="network_in" label="入站(KB/s)" min-width="120" />
            <el-table-column prop="network_out" label="出站(KB/s)" min-width="120" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/axios'

const instances = ref([])
const addInstanceDialogVisible = ref(false)
const editInstanceDialogVisible = ref(false)
const instanceDetailVisible = ref(false)
const saving = ref(false)
const updating = ref(false)
const editingInstanceId = ref(null)
const detailLoading = ref(false)
const instanceForm = reactive({
  name: '',
  host: '',
  port: 8080,
  api_key: '',
  group: '',
  description: ''
})
const editForm = reactive({
  name: '',
  host: '',
  port: 8080,
  api_key: '',
  group: '',
  description: ''
})
const detail = reactive({
  instance: null,
  metrics: [],
  tasks: []
})

const getProgressClass = (percentage) => {
  if (percentage < 70) return 'progress-success'
  if (percentage < 90) return 'progress-warning'
  return 'progress-danger'
}

const fetchInstances = async () => {
  try {
    const res = await api.get('/instances/')
    instances.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const saveInstance = async () => {
  if (!instanceForm.name || !instanceForm.host || !instanceForm.api_key) {
    ElMessage.warning('请填写实例名称、主机地址和API密钥')
    return
  }
  saving.value = true
  try {
    await api.post('/instances/', instanceForm)
    ElMessage.success('添加实例成功')
    addInstanceDialogVisible.value = false
    fetchInstances()
    // 重置表单
    Object.assign(instanceForm, {
      name: '',
      host: '',
      port: 8080,
      api_key: '',
      group: '',
      description: ''
    })
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    saving.value = false
  }
}

const editInstance = (row) => {
  editingInstanceId.value = row.id
  Object.assign(editForm, {
    name: row.name || '',
    host: row.host || '',
    port: row.port || 8080,
    api_key: '',
    group: row.group || '',
    description: row.description || ''
  })
  editInstanceDialogVisible.value = true
}

const updateInstance = async () => {
  if (!editingInstanceId.value) return
  if (!editForm.name || !editForm.host) {
    ElMessage.warning('请填写实例名称和主机地址')
    return
  }

  const payload = {
    name: editForm.name,
    host: editForm.host,
    port: editForm.port,
    group: editForm.group,
    description: editForm.description
  }
  if (editForm.api_key) {
    payload.api_key = editForm.api_key
  }

  updating.value = true
  try {
    await api.put(`/instances/${editingInstanceId.value}`, payload)
    ElMessage.success('实例已更新')
    editInstanceDialogVisible.value = false
    await fetchInstances()
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    updating.value = false
  }
}

const deleteInstance = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个实例吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/instances/${row.id}`)
    ElMessage.success('删除成功')
    fetchInstances()
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已在 axios 拦截器中处理
    }
  }
}

const viewInstance = (row) => {
  instanceDetailVisible.value = true
  detailLoading.value = true
  Promise.all([
    api.get(`/instances/${row.id}`),
    api.get(`/instances/${row.id}/metrics/`, { params: { limit: 10 } }),
    api.get(`/instances/${row.id}/tasks/`, { params: { limit: 10 } })
  ])
    .then(([instanceRes, metricsRes, tasksRes]) => {
      detail.instance = instanceRes.data
      detail.metrics = metricsRes.data
      detail.tasks = tasksRes.data
    })
    .catch(() => {
      detail.instance = null
      detail.metrics = []
      detail.tasks = []
    })
    .finally(() => {
      detailLoading.value = false
    })
}

onMounted(() => {
  fetchInstances()
})
</script>

<style scoped>
.instances-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.page-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: nowrap;
  white-space: nowrap;
}

.action-buttons .el-button {
  padding: 4px 6px;
  margin-left: 0;
}

.instance-detail {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-section h4 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 14px;
}
</style>
