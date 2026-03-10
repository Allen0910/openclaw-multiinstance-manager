<template>
  <div class="commands-page">
    <div class="page-header">
      <h1>OpenClaw 命令手册</h1>
      <p class="subtitle">OpenClaw 常用命令自查表 - 完整版</p>
    </div>

    <div class="search-box">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="搜索命令..."
        class="search-input"
      />
    </div>

    <div class="categories">
      <div 
        v-for="category in filteredCategories" 
        :key="category.name" 
        class="category-section"
      >
        <div class="category-header" @click="toggleCategory(category.name)">
          <h2>{{ category.name }}</h2>
          <span class="toggle-icon">{{ expandedCategories.includes(category.name) ? '−' : '+' }}</span>
        </div>
        
        <div v-show="expandedCategories.includes(category.name)" class="category-content">
          <table class="commands-table">
            <thead>
              <tr>
                <th>子项</th>
                <th>命令说明</th>
                <th>具体命令</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(cmd, index) in category.commands" :key="index">
                <td class="sub-item">{{ cmd.subItem }}</td>
                <td class="description">{{ cmd.description }}</td>
                <td class="command">
                  <code>{{ cmd.command }}</code>
                </td>
                <td class="actions">
                  <button class="copy-btn" @click="copyCommand(cmd.command)" title="复制命令">
                    <svg viewBox="0 0 24 24" width="16" height="16">
                      <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z" fill="currentColor"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 复制提示 -->
    <div v-if="showCopyTip" class="copy-tip">
      命令已复制到剪贴板
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const expandedCategories = ref(['一、快速入门'])
const showCopyTip = ref(false)

const categories = ref([
  {
    name: '一、快速入门',
    commands: [
      { subItem: '1.1', description: '查看所有命令', command: 'openclaw --help' },
      { subItem: '1.1', description: '查看版本号', command: 'openclaw --version' },
      { subItem: '1.1', description: '查看特定命令帮助', command: 'openclaw <command> --help' },
      { subItem: '1.1', description: '查看 config 命令帮助', command: 'openclaw config --help' },
      { subItem: '1.2', description: '首次安装后初始化配置', command: 'openclaw setup' },
      { subItem: '1.2', description: '交互式引导配置（推荐新手）', command: 'openclaw onboard' },
      { subItem: '1.2', description: '打开控制面板', command: 'openclaw dashboard' },
    ]
  },
  {
    name: '二、配置管理命令',
    commands: [
      { subItem: '2.1', description: '查看完整配置', command: 'openclaw config get' },
      { subItem: '2.1', description: '查看特定配置项', command: 'openclaw config get models.default' },
      { subItem: '2.1', description: '查看特定配置项', command: 'openclaw config get providers.mistral.apiKey' },
      { subItem: '2.1', description: '查看特定部分配置', command: 'openclaw config get --section models' },
      { subItem: '2.1', description: '查看特定部分配置', command: 'openclaw config get --section providers' },
      { subItem: '2.2', description: '设置默认模型', command: 'openclaw config set models.default mistral:mixtral-8x7b' },
      { subItem: '2.2', description: '设置快速模型', command: 'openclaw config set models.fast mistral:mistral-7b' },
      { subItem: '2.2', description: '配置 Mistral API Key', command: 'openclaw config set providers.mistral.apiKey YOUR_API_KEY_HERE' },
      { subItem: '2.2', description: '启用缓存', command: 'openclaw config set cache.enabled true' },
      { subItem: '2.2', description: '设置缓存大小', command: 'openclaw config set cache.maxSize 5000' },
      { subItem: '2.3', description: '删除特定配置项', command: 'openclaw config unset models.fast' },
      { subItem: '2.3', description: '重置某个节点', command: 'openclaw config unset models' },
      { subItem: '2.4', description: '打开完整配置向导', command: 'openclaw configure' },
      { subItem: '2.4', description: '打开特定部分配置向导', command: 'openclaw configure --section models' },
      { subItem: '2.4', description: '打开特定部分配置向导', command: 'openclaw configure --section providers' },
      { subItem: '2.4', description: '打开特定部分配置向导', command: 'openclaw configure --section channels' },
    ]
  },
  {
    name: '三、Gateway 控制命令',
    commands: [
      { subItem: '3.1', description: '启动 Gateway（默认端口 18789）', command: 'openclaw gateway start' },
      { subItem: '3.1', description: '自定义端口启动', command: 'openclaw gateway start --port 19000' },
      { subItem: '3.1', description: '强制启动（杀死占用进程）', command: 'openclaw gateway start --force' },
      { subItem: '3.1', description: '停止 Gateway', command: 'openclaw gateway stop' },
      { subItem: '3.1', description: '重启 Gateway', command: 'openclaw gateway restart' },
      { subItem: '3.1', description: '查看运行状态', command: 'openclaw gateway status' },
      { subItem: '3.2', description: '前台运行 Gateway（调试用）', command: 'openclaw gateway' },
      { subItem: '3.2', description: '开发模式运行（隔离状态）', command: 'openclaw --dev gateway' },
      { subItem: '3.2', description: '查看健康状态', command: 'openclaw health' },
      { subItem: '3.3', description: '查看实时日志', command: 'openclaw logs' },
      { subItem: '3.3', description: '查看最近 50 行日志', command: 'openclaw logs --lines 50' },
      { subItem: '3.3', description: '查看错误日志', command: 'openclaw logs --filter error' },
      { subItem: '3.3', description: '持续监控日志', command: 'openclaw logs --follow' },
      { subItem: '3.4', description: 'systemd 管理（生产环境）', command: 'sudo systemctl start openclaw-gateway' },
      { subItem: '3.4', description: 'systemd 管理', command: 'sudo systemctl stop openclaw-gateway' },
      { subItem: '3.4', description: 'systemd 管理', command: 'sudo systemctl restart openclaw-gateway' },
      { subItem: '3.4', description: 'systemd 管理', command: 'sudo systemctl status openclaw-gateway' },
      { subItem: '3.4', description: '开机自启动', command: 'sudo systemctl enable openclaw-gateway' },
    ]
  },
  {
    name: '四、消息发送命令',
    commands: [
      { subItem: '4.1', description: '发送消息到当前会话', command: 'openclaw message send --message "Hello"' },
      { subItem: '4.1', description: '发送到 Telegram', command: 'openclaw message send --channel telegram --target @mychat --message "Hello from OpenClaw"' },
      { subItem: '4.1', description: '发送到 WhatsApp', command: 'openclaw message send --channel whatsapp --target +8613800138000 --message "您好"' },
      { subItem: '4.1', description: '发送到 Slack 频道', command: 'openclaw message send --channel slack --target C1234567890 --message "@channel 重要通知"' },
      { subItem: '4.2', description: '发送图片', command: 'openclaw message send --channel telegram --target @mychat --media /tmp/photo.jpg --caption "这是一张图片"' },
      { subItem: '4.2', description: '发送音频', command: 'openclaw message send --channel whatsapp --target +8613800138000 --media /tmp/voice.mp3' },
      { subItem: '4.2', description: '发送文档', command: 'openclaw message send --channel telegram --target @mychat --media /tmp/report.pdf' },
      { subItem: '4.3', description: '发送 JSON 格式（脚本自动化）', command: 'openclaw message send --target @mychat --message "Hello" --json' },
      { subItem: '4.3', description: '回复消息', command: 'openclaw message send --target @mychat --message "收到" --replyTo 12345' },
      { subItem: '4.3', description: '指定频道', command: 'openclaw message send --channel discord --target channel:1234567890 --message "Hello"' },
      { subItem: '4.4', description: '创建投票（Telegram）', command: 'openclaw message send --channel telegram --target @mychat --pollQuestion "OpenClaw 好用吗？" --pollOption 非常好用 --pollOption 一般 --pollOption 还需要改进 --pollDurationHours 24' },
      { subItem: '4.4', description: '发送反应（Discord）', command: 'openclaw message send --channel discord --messageId 1234567890 --emoji 👍 --action react' },
    ]
  },
  {
    name: '五、技能管理命令',
    commands: [
      { subItem: '5.1', description: '查看所有已安装技能', command: 'openclaw skills list' },
      { subItem: '5.1', description: '搜索技能', command: 'openclaw skills search weather' },
      { subItem: '5.1', description: '查看技能详情', command: 'openclaw skills show weather' },
      { subItem: '5.2', description: '安装技能', command: 'openclaw skills install weather' },
      { subItem: '5.2', description: '从指定来源安装', command: 'openclaw skills install weather --source github' },
      { subItem: '5.2', description: '指定版本安装', command: 'openclaw skills install weather@1.2.0' },
      { subItem: '5.2', description: '卸载技能', command: 'openclaw skills uninstall weather' },
      { subItem: '5.3', description: '更新所有技能', command: 'openclaw skills update' },
      { subItem: '5.3', description: '更新特定技能', command: 'openclaw skills update weather' },
      { subItem: '5.3', description: '同步技能', command: 'openclaw skills sync' },
      { subItem: '5.4', description: '创建新技能', command: 'openclaw skills create my-skill' },
      { subItem: '5.4', description: '验证技能', command: 'openclaw skills validate my-skill' },
      { subItem: '5.4', description: '打包技能', command: 'openclaw skills pack my-skill' },
    ]
  },
  {
    name: '六、模型配置命令',
    commands: [
      { subItem: '6.1', description: '查看所有配置的模型', command: 'openclaw models list' },
      { subItem: '6.1', description: '查看默认模型', command: 'openclaw models default' },
      { subItem: '6.1', description: '查看模型详情', command: 'openclaw models show mistral:mixtral-8x7b' },
      { subItem: '6.2', description: '设置默认模型', command: 'openclaw models set-default mistral:mixtral-8x7b' },
      { subItem: '6.2', description: '添加新模型', command: 'openclaw models add --name my-model --provider mistral --id mistral-medium --maxTokens 8192' },
      { subItem: '6.2', description: '测试模型', command: 'openclaw models test --model mistral:mixtral-8x7b --prompt "Hello, OpenClaw!"' },
      { subItem: '6.3', description: '临时指定模型', command: 'openclaw agent --model mistral:mistral-7b --message "快速响应"' },
      { subItem: '6.3', description: '使用内置模型别名', command: 'openclaw agent --model fast --message "这个用fast模型"' },
    ]
  },
  {
    name: '七、频道管理命令',
    commands: [
      { subItem: '7.1', description: '查看所有配置的频道', command: 'openclaw channels list' },
      { subItem: '7.1', description: '查看频道状态', command: 'openclaw channels status' },
      { subItem: '7.1', description: '查看特定频道详情', command: 'openclaw channels show telegram' },
      { subItem: '7.2', description: 'Telegram 登录', command: 'openclaw channels login --channel telegram' },
      { subItem: '7.2', description: 'WhatsApp 登录', command: 'openclaw channels login --channel whatsapp --verbose' },
      { subItem: '7.2', description: 'Slack 登录', command: 'openclaw channels login --channel slack' },
      { subItem: '7.2', description: 'Discord 登录', command: 'openclaw channels login --channel discord' },
      { subItem: '7.3', description: '测试频道连接', command: 'openclaw channels test --channel telegram' },
      { subItem: '7.3', description: '发送测试消息', command: 'openclaw channels test --channel telegram --target @mychat --message "测试消息"' },
      { subItem: '7.4', description: '配置频道', command: 'openclaw channels configure --channel telegram' },
      { subItem: '7.4', description: '更新频道 Token', command: 'openclaw channels update --channel telegram --token NEW_TOKEN' },
      { subItem: '7.4', description: '启用频道', command: 'openclaw channels enable telegram' },
      { subItem: '7.4', description: '禁用频道', command: 'openclaw channels disable telegram' },
    ]
  },
  {
    name: '八、会话管理命令',
    commands: [
      { subItem: '8.1', description: '列出所有会话', command: 'openclaw sessions' },
      { subItem: '8.1', description: '列出活跃会话', command: 'openclaw sessions --active' },
      { subItem: '8.1', description: '列出特定频道的会话', command: 'openclaw sessions --channel telegram' },
      { subItem: '8.1', description: '显示最近 10 个会话', command: 'openclaw sessions --limit 10' },
      { subItem: '8.2', description: '查看特定会话的历史', command: 'openclaw sessions history <session-key>' },
      { subItem: '8.2', description: '查看最近的消息', command: 'openclaw sessions history <session-key> --limit 20' },
      { subItem: '8.2', description: '导出会话历史', command: 'openclaw sessions history <session-key> --export > history.json' },
      { subItem: '8.3', description: '发送消息到会话', command: 'openclaw sessions send --session <session-key> --message "你好"' },
      { subItem: '8.3', description: '重置会话', command: 'openclaw sessions reset <session-key>' },
      { subItem: '8.3', description: '删除会话', command: 'openclaw sessions delete <session-key>' },
    ]
  },
  {
    name: '九、节点管理命令',
    commands: [
      { subItem: '9.1', description: '查看所有配对的节点', command: 'openclaw nodes list' },
      { subItem: '9.1', description: '查看节点状态', command: 'openclaw nodes status' },
      { subItem: '9.1', description: '描述节点详情', command: 'openclaw nodes describe <node-id>' },
      { subItem: '9.2', description: '发送通知到节点', command: 'openclaw nodes notify --node my-phone --title "提醒" --body "该吃饭了"' },
      { subItem: '9.2', description: '设置推送优先级', command: 'openclaw nodes notify --node my-phone --priority timeSensitive --title "紧急通知" --body "快递到了"' },
      { subItem: '9.2', description: '查看相册（手机）', command: 'openclaw nodes camera-list --node my-phone' },
      { subItem: '9.2', description: '拍照', command: 'openclaw nodes camera-snap --node my-phone --facing back --output /tmp/photo.jpg' },
      { subItem: '9.3', description: '启动配对', command: 'openclaw node pairing start' },
      { subItem: '9.3', description: '查看待配对节点', command: 'openclaw nodes pending' },
      { subItem: '9.3', description: '批准配对', command: 'openclaw nodes approve --node <node-id>' },
      { subItem: '9.3', description: '拒绝配对', command: 'openclaw nodes reject --node <node-id>' },
    ]
  },
  {
    name: '十、记忆管理命令',
    commands: [
      { subItem: '10.1', description: '搜索记忆', command: 'openclaw memory search "OpenClaw 配置"' },
      { subItem: '10.1', description: '搜索并显示多行上下文', command: 'openclaw memory search "配置" --lines 5' },
      { subItem: '10.1', description: '搜索特定路径的记忆', command: 'openclaw memory search "配置" --path MEMORY.md' },
      { subItem: '10.1', description: '限制结果数量', command: 'openclaw memory search "配置" --maxResults 10' },
      { subItem: '10.2', description: '查看记忆统计', command: 'openclaw memory stats' },
      { subItem: '10.2', description: '清理过期记忆', command: 'openclaw memory clean' },
      { subItem: '10.2', description: '备份记忆', command: 'openclaw memory backup --output /tmp/memory-backup.json' },
    ]
  },
  {
    name: '十一、Cron 定时任务命令',
    commands: [
      { subItem: '11.1', description: '列出所有任务', command: 'openclaw cron list' },
      { subItem: '11.1', description: '查看任务运行历史', command: 'openclaw cron runs <job-id>' },
      { subItem: '11.1', description: '查看调度器状态', command: 'openclaw cron status' },
      { subItem: '11.2', description: '每天凌晨触发', command: 'openclaw cron add --name "daily-report" --schedule "0 0 * * *" --text "生成每日报告"' },
      { subItem: '11.2', description: '每 30 分钟触发', command: 'openclaw cron add --name "check-notifications" --schedule "*/30 * * * *" --text "检查通知"' },
      { subItem: '11.2', description: '单次任务（特定时间）', command: 'openclaw cron add --name "special-task" --schedule "at" --at "2026-03-01T10:00:00" --text "执行特殊任务"' },
      { subItem: '11.3', description: '立即运行任务', command: 'openclaw cron run <job-id>' },
      { subItem: '11.3', description: '更新任务', command: 'openclaw cron update <job-id> --schedule "0 6 * * *"' },
      { subItem: '11.3', description: '删除任务', command: 'openclaw cron remove <job-id>' },
      { subItem: '11.3', description: '发送唤醒事件', command: 'openclaw cron wake --text "检查新消息"' },
    ]
  },
  {
    name: '十二、系统命令',
    commands: [
      { subItem: '12.1', description: '运行健康检查', command: 'openclaw doctor' },
      { subItem: '12.1', description: '快速修复常见问题', command: 'openclaw doctor --fix' },
      { subItem: '12.1', description: '检查特定组件', command: 'openclaw doctor --check gateway' },
      { subItem: '12.1', description: '检查特定组件', command: 'openclaw doctor --check channels' },
      { subItem: '12.2', description: '查看频道健康状态', command: 'openclaw status' },
      { subItem: '12.2', description: '查看系统事件', command: 'openclaw system events' },
      { subItem: '12.2', description: '查看心跳状态', command: 'openclaw system heartbeat' },
      { subItem: '12.3', description: '运行安全检查', command: 'openclaw security audit' },
      { subItem: '12.3', description: '检查权限配置', command: 'openclaw security check-permissions' },
      { subItem: '12.3', description: '检查 API Key 有效性', command: 'openclaw security verify-keys' },
    ]
  },
  {
    name: '十三、插件管理命令',
    commands: [
      { subItem: '13.1', description: '查看已安装插件', command: 'openclaw plugins list' },
      { subItem: '13.1', description: '查看插件详情', command: 'openclaw plugins show <plugin-name>' },
      { subItem: '13.1', description: '检查插件状态', command: 'openclaw plugins status' },
      { subItem: '13.2', description: '启用插件', command: 'openclaw plugins enable feishu' },
      { subItem: '13.2', description: '禁用插件', command: 'openclaw plugins disable feishu' },
      { subItem: '13.2', description: '重启插件', command: 'openclaw plugins restart feishu' },
      { subItem: '13.2', description: '更新插件', command: 'openclaw plugins update' },
    ]
  },
  {
    name: '十四、浏览器控制命令',
    commands: [
      { subItem: '14.1', description: '启动浏览器', command: 'openclaw browser start' },
      { subItem: '14.1', description: '停止浏览器', command: 'openclaw browser stop' },
      { subItem: '14.1', description: '切换配置', command: 'openclaw browser start --profile chrome' },
      { subItem: '14.1', description: '切换配置', command: 'openclaw browser start --profile openclaw' },
      { subItem: '14.2', description: '打开网页', command: 'openclaw browser open https://example.com' },
      { subItem: '14.2', description: '截图', command: 'openclaw browser screenshot --output /tmp/screenshot.png' },
      { subItem: '14.2', description: '获取快照', command: 'openclaw browser snapshot --target main' },
      { subItem: '14.2', description: '查看标签页', command: 'openclaw browser tabs' },
    ]
  },
  {
    name: '十五、更新与维护命令',
    commands: [
      { subItem: '15.1', description: '查看更新', command: 'openclaw update --dry-run' },
      { subItem: '15.1', description: '执行更新', command: 'openclaw update' },
      { subItem: '15.1', description: '更新到特定版本', command: 'openclaw update --tag 2026.2.22' },
      { subItem: '15.1', description: '更新到 Beta 版', command: 'openclaw update --channel beta' },
      { subItem: '15.2', description: '备份配置', command: 'cp ~/.openclaw/config.json ~/.openclaw/config.json.backup' },
      { subItem: '15.2', description: '重置配置（保留 CLI）', command: 'openclaw reset' },
      { subItem: '15.2', description: '完全卸载（包括数据）', command: 'openclaw uninstall' },
      { subItem: '15.3', description: '生成 Bash 补全脚本', command: 'openclaw completion bash > ~/.openclaw-completion' },
      { subItem: '15.3', description: '生成 Zsh 补全脚本', command: 'openclaw completion zsh > ~/.zsh-completion' },
      { subItem: '15.3', description: '应用补全（Bash）', command: 'echo "source ~/.openclaw-completion" >> ~/.bashrc' },
      { subItem: '15.3', description: '应用补全（Bash）', command: 'source ~/.bashrc' },
    ]
  },
  {
    name: '十六、常用组合命令',
    commands: [
      { subItem: '16.1', description: '一键创建、开发、测试技能', command: 'openclaw skills create my-new-skill && cd ~/.openclaw/workspace/skills/my-new-skill && vim SKILL.md' },
      { subItem: '16.2', description: '发送到多个目标', command: 'openclaw message send --target @user1 --message "通知内容"' },
      { subItem: '16.2', description: '使用循环批量发送', command: 'for target in user1 user2 user3; do openclaw message send --target @$target --message "通知内容"; done' },
      { subItem: '16.3', description: '重启并验证', command: 'openclaw gateway restart && sleep 5 && openclaw gateway status && openclaw health' },
      { subItem: '16.4', description: '安全更新流程', command: 'cp ~/.openclaw/config.json ~/.openclaw/config.json.backup && openclaw update --dry-run && openclaw update && openclaw gateway restart' },
      { subItem: '16.5', description: '生成每日报告（Cron 脚本）', command: '0 9 * * * openclaw cron add --name daily-report --schedule "0 9 * * *" --text "生成昨日数据分析报告"' },
    ]
  },
  {
    name: '十七、故障排除命令',
    commands: [
      { subItem: '17.1', description: '检查端口占用', command: 'sudo lsof -i :18789' },
      { subItem: '17.1', description: '强制重启', command: 'openclaw gateway start --force' },
      { subItem: '17.1', description: '查看错误日志', command: 'openclaw logs --filter error' },
      { subItem: '17.1', description: '运行健康检查', command: 'openclaw doctor' },
      { subItem: '17.2', description: '检查频道状态', command: 'openclaw channels status' },
      { subItem: '17.2', description: '测试频道', command: 'openclaw channels test --channel telegram' },
      { subItem: '17.2', description: '重新登录频道', command: 'openclaw channels login --channel telegram' },
      { subItem: '17.2', description: '查看详细日志', command: 'openclaw message send --target @mychat --message "Test" --verbose' },
      { subItem: '17.3', description: '检查 API Key', command: 'openclaw config get providers.openai.apiKey' },
      { subItem: '17.3', description: '测试模型', command: 'openclaw models test --model mistral:mixtral-8x7b --prompt "test"' },
      { subItem: '17.3', description: '检查网络连接', command: 'ping api.openai.com' },
      { subItem: '17.3', description: '运行诊断', command: 'openclaw doctor --check models' },
      { subItem: '17.4', description: '检查技能列表', command: 'openclaw skills list' },
      { subItem: '17.4', description: '验证技能', command: 'openclaw skills validate my-skill' },
      { subItem: '17.4', description: '重新安装技能', command: 'openclaw skills uninstall my-skill && openclaw skills install my-skill' },
      { subItem: '17.4', description: '查看错误日志', command: 'openclaw logs --filter skill' },
    ]
  },
  {
    name: '十八、生产环境最佳实践',
    commands: [
      { subItem: '18.1', description: '存储敏感信息', command: 'export OPENAI_API_KEY="sk-xxx"' },
      { subItem: '18.1', description: '启动 Gateway', command: 'openclaw gateway start' },
      { subItem: '18.2', description: '限制配置文件权限', command: 'chmod 600 ~/.openclaw/config.json' },
      { subItem: '18.2', description: '检查权限', command: 'ls -la ~/.openclaw/config.json' },
    ]
  }
])

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value
  
  const query = searchQuery.value.toLowerCase()
  return categories.value.map(cat => ({
    ...cat,
    commands: cat.commands.filter(cmd => 
      cmd.description.toLowerCase().includes(query) ||
      cmd.command.toLowerCase().includes(query)
    )
  })).filter(cat => cat.commands.length > 0)
})

const toggleCategory = (name) => {
  const index = expandedCategories.value.indexOf(name)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(name)
  }
}

const copyCommand = async (command) => {
  try {
    await navigator.clipboard.writeText(command)
    showCopyTip.value = true
    setTimeout(() => {
      showCopyTip.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.commands-page {
  padding: 20px;
  background: #0a0e17;
  min-height: 100vh;
  color: #e0e0e0;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #00d4ff;
  margin-bottom: 10px;
}

.subtitle {
  color: #888;
  font-size: 14px;
}

.search-box {
  max-width: 600px;
  margin: 0 auto 30px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  background: #1a1f2e;
  border: 1px solid #2a3142;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #00d4ff;
}

.categories {
  max-width: 1200px;
  margin: 0 auto;
}

.category-section {
  margin-bottom: 15px;
  background: #111620;
  border-radius: 8px;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #1a2235;
  cursor: pointer;
  transition: background 0.2s;
}

.category-header:hover {
  background: #232d42;
}

.category-header h2 {
  font-size: 16px;
  color: #00d4ff;
  margin: 0;
}

.toggle-icon {
  font-size: 20px;
  color: #00d4ff;
}

.category-content {
  padding: 15px;
}

.commands-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.commands-table th {
  text-align: left;
  padding: 10px;
  background: #0d1117;
  color: #888;
  font-weight: 500;
  border-bottom: 1px solid #2a3142;
}

.commands-table td {
  padding: 10px;
  border-bottom: 1px solid #1f2633;
}

.commands-table tr:hover {
  background: #1a2235;
}

.sub-item {
  color: #666;
  width: 60px;
}

.description {
  color: #aaa;
}

.command {
  font-family: 'Consolas', 'Monaco', monospace;
}

.command code {
  background: #0d1117;
  padding: 4px 8px;
  border-radius: 4px;
  color: #7dd3fc;
  font-size: 12px;
}

.actions {
  width: 50px;
  text-align: center;
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background 0.2s;
}

.copy-btn:hover {
  background: #2a3142;
}

.copy-btn svg {
  color: #00d4ff;
}

.copy-tip {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: #00d4ff;
  color: #000;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
