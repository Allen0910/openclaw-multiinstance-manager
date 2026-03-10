# OpenClaw 多实例监控管理系统

## 项目介绍
基于BS架构的OpenClaw多实例统一管理平台，支持实时监控、批量操作、配置管理、任务调度等功能。

## 功能特性
- 🖥️ 多实例状态总览，实时监控CPU/内存/磁盘使用率
- 🔧 远程实例管理，支持一键启动/停止/重启/升级
- 📊 运行数据统计，技能使用情况、任务执行历史分析
- ⚠️ 智能告警中心，支持多渠道告警推送
- 📦 统一配置管理，批量同步配置和技能
- ⏰ 定时任务调度，支持批量任务下发

## 技术栈
- **前端**：Vue3 + Element Plus + ECharts
- **后端**：FastAPI + SQLAlchemy + WebSocket
- **数据库**：MySQL + Redis
- **部署**：Docker + Docker Compose

## 项目结构
```
openclaw-manager/
├── backend/          # 后端服务
│   ├── app/          # 应用代码
│   ├── requirements.txt
│   └── main.py
├── frontend/         # 前端页面
│   ├── src/
│   └── package.json
├── docker/           # Docker配置
├── docs/             # 文档
└── README.md
```
