<template>
  <div class="skills-page">
    <div class="page-header">
      <h2>技能市场</h2>
      <el-button type="primary" class="btn-primary" @click="refreshSkills">
        <el-icon><Refresh /></el-icon>
        刷新列表
      </el-button>
    </div>

    <div class="skills-grid">
      <div class="skill-card card-glow" v-for="skill in skills" :key="skill.id">
        <div class="skill-header">
          <div class="skill-name">
            <el-icon size="20"><Box /></el-icon>
            <span>{{ skill.name }}</span>
          </div>
          <el-tag type="info" size="small">v{{ skill.version }}</el-tag>
        </div>
        <p class="skill-description">{{ skill.description || '暂无描述' }}</p>
        <div class="skill-meta">
          <span><el-icon><User /></el-icon> {{ skill.author || 'unknown' }}</span>
          <span><el-icon><Download /></el-icon> {{ skill.installed_count }}</span>
        </div>
        <el-button
          type="primary"
          class="btn-primary"
          style="width: 100%"
          :loading="installingSkillId === skill.id"
          @click="installSkill(skill)"
        >
          <el-icon><Plus /></el-icon>
          安装
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/axios'

const skills = ref([])
const installingSkillId = ref(null)

const fetchSkills = async () => {
  try {
    const res = await api.get('/skills/', {
      params: { limit: 200 }
    })
    skills.value = res.data
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  }
}

const refreshSkills = async () => {
  await fetchSkills()
  ElMessage.success('刷新成功')
}

const installSkill = async (skill) => {
  installingSkillId.value = skill.id
  try {
    const res = await api.post(`/skills/${skill.id}/install`, {})
    ElMessage.success(res.data.message || `技能 ${skill.name} 安装完成`)
    await fetchSkills()
  } catch (error) {
    // 错误已在 axios 拦截器中处理
  } finally {
    installingSkillId.value = null
  }
}

onMounted(() => {
  fetchSkills()
})
</script>

<style scoped>
.skills-page {
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

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.skill-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skill-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.skill-description {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 12px;
  min-height: 40px;
  line-height: 1.5;
}

.skill-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.skill-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
