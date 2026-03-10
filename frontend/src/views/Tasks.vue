<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>任务管理</h2>
      <el-button type="primary" class="btn-primary" @click="createTaskDialogVisible = true">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
    </div>

    <div class="card-glow">
      <div class="table-custom">
        <el-table :data="tasks" border stripe style="width: 100%">
          <el-table-column prop="name" label="任务名称" min-width="220" />
          <el-table-column prop="instance_id" label="实例ID" width="100" />
          <el-table-column prop="type" label="任务类型" width="120">
            <template #default="scope">
              <el-tag size="small" :type="getTypeTag(scope.row.type)">
                {{ getTypeText(scope.row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" class="tag-success" size="small">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180" />
          <el-table-column prop="started_at" label="开始时间" min-width="180" />
          <el-table-column prop="finished_at" label="结束时间" min-width="180" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-button size="small" type="primary" link @click="viewResult(scope.row)">
                  <el-icon><View /></el-icon>
                  查看结果
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  link
                  :disabled="['success', 'failed', 'canceled'].includes(scope.row.status)"
                  @click="cancelTask(scope.row)"
                >
                  <el-icon><Close /></el-icon>
                  取消
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-dialog v-model="createTaskDialogVisible" title="创建任务" width="500px" class="dialog-custom">
      <el-form :model="taskForm" label-width="80px" class="form-custom">
        <el-form-item label="实例" prop="instance_id">
          <el-select v-model="taskForm.instance_id" placeholder="请选择实例" style="width: 100%">
            <el-option v-for="instance in instances" :key="instance.id" :label="instance.name" :value="instance.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="taskForm.type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="执行命令" value="command" />
            <el-option label="调用技能" value="skill" />
            <el-option label="升级版本" value="upgrade" />
            <el-option label="安装技能" value="install_skill" />
            <el-option label="重启实例" value="restart" />
          </el-select>
        </el-form-item>
        <el-form-item label="参数" prop="params">
          <el-input v-model="taskParams" type="textarea" :rows="4" placeholder="请输入JSON格式参数" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTaskDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary" @click="createTask" :loading="creating">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resultDialogVisible" title="任务结果" width="700px" class="dialog-custom">
      <pre class="result-pre">{{ taskResult }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

const tasks = ref([])
const instances = ref([])
const createTaskDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const creating = ref(false)
const taskResult = ref('')
const taskParams = ref('{}')
const taskForm = reactive({
  instance_id: null,
  name: '',
  type: '',
  params: {}
})

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    canceled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待执行',
    running: '运行中',
    success: '成功',
    failed: '失败',
    canceled: '已取消'
  }
  return texts[status] || status
}

const getTypeTag = (type) => {
  const types = {
    command: 'primary',
    skill: 'success',
    upgrade: 'warning',
    install_skill: 'success',
    restart: 'danger'
  }
  return types[type] || 'info'
}

const getTypeText = (type) => {
  const texts = {
    command: '执行命令',
    skill: '调用技能',
    upgrade: '升级版本',
    install_skill: '安装技能',
    restart: '重启实例'
  }
  return texts[type] || type
}

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks/', {
      params: { limit: 200 }
    })
    tasks.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const fetchInstances = async () => {
  try {
    const res = await api.get('/instances/')
    instances.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const createTask = async () => {
  creating.value = true
  try {
    taskForm.params = JSON.parse(taskParams.value)
    await api.post('/tasks/', taskForm)
    ElMessage.success('任务创建成功')
    createTaskDialogVisible.value = false
    await fetchTasks()
    Object.assign(taskForm, {
      instance_id: null,
      name: '',
      type: '',
      params: {}
    })
    taskParams.value = '{}'
  } catch (error) {
    if (error instanceof SyntaxError) {
      ElMessage.error('JSON格式错误')
    }
  } finally {
    creating.value = false
  }
}

const viewResult = (row) => {
  taskResult.value = row.result || '暂无结果'
  resultDialogVisible.value = true
}

const cancelTask = async (row) => {
  if (['success', 'failed', 'canceled'].includes(row.status)) {
    ElMessage.info('任务已结束，无法取消')
    return
  }
  try {
    await api.post(`/tasks/${row.id}/cancel`)
    ElMessage.success('任务已取消')
    await fetchTasks()
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

onMounted(() => {
  fetchTasks()
  fetchInstances()
})
</script>

<style scoped>
.tasks-page {
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

.result-pre {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}
</style>
