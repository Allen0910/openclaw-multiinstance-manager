<template>
  <div class="alerts-page">
    <div class="page-header">
      <h2>告警中心</h2>
      <el-button type="primary" class="btn-primary" @click="markAllAsRead">
        <el-icon><Check /></el-icon>
        全部已读
      </el-button>
    </div>

    <div class="card-glow">
      <div class="table-custom">
        <el-table :data="alerts" border stripe>
          <el-table-column prop="level" label="级别" width="100">
            <template #default="scope">
              <el-tag :type="getLevelType(scope.row.level)" size="small">
                {{ getLevelText(scope.row.level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="content" label="内容" min-width="300" />
          <el-table-column prop="instance_id" label="实例ID" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'unread' ? 'warning' : 'info'" class="tag-info" size="small">
                {{ scope.row.status === 'unread' ? '未读' : '已处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-button size="small" type="warning" link @click="markAsRead(scope.row)" v-if="scope.row.status === 'unread'">
                  <el-icon><Check /></el-icon>
                  标记已读
                </el-button>
                <el-button size="small" type="primary" link @click="viewDetail(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/axios'

const alerts = ref([])

const getLevelType = (level) => {
  const types = {
    info: 'info',
    warning: 'warning',
    error: 'danger',
    critical: 'danger'
  }
  return types[level] || 'info'
}

const getLevelText = (level) => {
  const texts = {
    info: '信息',
    warning: '警告',
    error: '错误',
    critical: '严重'
  }
  return texts[level] || level
}

const fetchAlerts = async () => {
  try {
    const res = await api.get('/alerts/', {
      params: { limit: 200 }
    })
    alerts.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const markAsRead = async (row) => {
  try {
    const res = await api.put(`/alerts/${row.id}`, { status: 'resolved', resolved_at: new Date().toISOString() })
    const index = alerts.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      alerts.value[index] = res.data
    }
    ElMessage.success('标记成功')
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const markAllAsRead = async () => {
  try {
    await ElMessageBox.confirm('确定要将所有告警标记为已读吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const unreadAlerts = alerts.value.filter(alert => alert.status === 'unread')
    await Promise.all(
      unreadAlerts.map(alert =>
        api.put(`/alerts/${alert.id}`, { status: 'resolved', resolved_at: new Date().toISOString() })
      )
    )

    await fetchAlerts()
    ElMessage.success('全部已读')
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已在 axios 拦截器中处理
    }
  }
}

const viewDetail = (row) => {
  ElMessageBox.alert(row.content, '告警详情', {
    confirmButtonText: '确定'
  })
}

onMounted(() => {
  fetchAlerts()
})
</script>

<style scoped>
.alerts-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .el-button {
  padding: 4px 8px;
}
</style>
