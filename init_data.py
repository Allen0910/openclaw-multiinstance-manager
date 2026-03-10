#!/usr/bin/env python3
"""
初始化测试数据脚本
创建默认实例和模拟数据
"""
import os
import random
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, "backend"))

from app import crud, schemas
from app.database import SessionLocal


def init_default_instances():
    """初始化默认实例"""
    db = SessionLocal()
    try:
        instances = crud.get_instances(db)
        if instances:
            print("实例已存在，跳过初始化")
            return

        instance1 = schemas.InstanceCreate(
            name="生产环境-01",
            host="192.168.1.100",
            port=8080,
            api_key="your-api-key-1",
            group="生产环境",
            description="主生产环境实例",
        )
        created1 = crud.create_instance(db, instance1)

        instance2 = schemas.InstanceCreate(
            name="测试环境-01",
            host="192.168.1.101",
            port=8080,
            api_key="your-api-key-2",
            group="测试环境",
            description="测试环境实例",
        )
        created2 = crud.create_instance(db, instance2)

        print("默认实例创建成功")

        generate_history_data(db, created1.id)
        generate_history_data(db, created2.id)
        init_default_tasks(db, [created1.id, created2.id])
        init_default_alerts(db, [created1.id, created2.id])
        init_default_skills(db)

    finally:
        db.close()


def generate_history_data(db, instance_id, hours=24):
    """生成历史监控数据"""
    print(f"生成实例{instance_id}的{hours}小时历史数据")

    for _ in range(hours * 4):  # 每15分钟一个点
        cpu = random.uniform(20, 80)
        memory = random.uniform(40, 90)
        disk = random.uniform(50, 85)
        network_in = random.uniform(100, 1000)
        network_out = random.uniform(200, 1500)
        task_count = random.randint(0, 5)

        metric = schemas.MetricCreate(
            instance_id=instance_id,
            cpu_usage=cpu,
            memory_usage=memory,
            disk_usage=disk,
            network_in=network_in,
            network_out=network_out,
            task_count=task_count,
        )
        crud.create_metric(db, metric)

        crud.update_instance_heartbeat(
            db,
            instance_id,
            {
                "cpu_usage": cpu,
                "memory_usage": memory,
                "disk_usage": disk,
                "version": "v1.0.0",
            },
        )

    print(f"实例{instance_id}历史数据生成完成")


def init_default_tasks(db, instance_ids):
    """初始化示例任务"""
    tasks = crud.get_tasks(db, limit=1)
    if tasks:
        print("任务数据已存在，跳过初始化")
        return

    task_specs = [
        ("日常巡检", "command", {"command": "openclaw status"}, "success", "巡检完成，所有实例状态正常"),
        ("拉取告警", "command", {"command": "openclaw alerts list --unread"}, "success", "已拉取告警列表"),
        ("健康检查", "command", {"command": "openclaw task run health-check"}, "success", "健康检查通过"),
    ]
    for index, instance_id in enumerate(instance_ids):
        for name, task_type, params, status, result in task_specs:
            task = schemas.TaskCreate(
                instance_id=instance_id,
                name=f"{name}-{index + 1}",
                type=task_type,
                params=params,
            )
            created = crud.create_task(db, task)
            crud.update_task(
                db,
                created.id,
                schemas.TaskUpdate(
                    status=status,
                    started_at=datetime.utcnow() - timedelta(minutes=random.randint(30, 300)),
                    finished_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 20)),
                    result=result,
                ),
            )
    print("默认任务创建完成")


def init_default_alerts(db, instance_ids):
    """初始化示例告警"""
    alerts = crud.get_alerts(db, limit=1)
    if alerts:
        print("告警数据已存在，跳过初始化")
        return

    alert_specs = [
        ("warning", "CPU使用率偏高", "CPU使用率超过80%，建议排查高负载进程"),
        ("warning", "内存使用率偏高", "内存使用率超过75%，建议扩容"),
        ("info", "磁盘清理建议", "检测到可清理日志文件，建议定期清理"),
    ]
    for index, instance_id in enumerate(instance_ids):
        for level, title, content in alert_specs:
            alert = schemas.AlertCreate(
                instance_id=instance_id,
                level=level,
                title=f"{title}-{index + 1}",
                content=content,
            )
            created = crud.create_alert(db, alert)
            if random.random() > 0.5:
                crud.update_alert(
                    db,
                    created.id,
                    schemas.AlertUpdate(status="resolved", resolved_at=datetime.utcnow() - timedelta(minutes=5)),
                )
    print("默认告警创建完成")


def init_default_skills(db):
    """初始化示例技能"""
    skills = crud.get_skills(db, limit=1)
    if skills:
        print("技能数据已存在，跳过初始化")
        return

    skill_specs = [
        ("system-inspector", "系统巡检技能", "v1.2.0", "OpenClaw Team"),
        ("log-analyzer", "日志分析技能", "v2.1.0", "OpenClaw Team"),
        ("auto-remediator", "自动修复技能", "v0.9.3", "Community"),
    ]
    for name, description, version, author in skill_specs:
        skill = schemas.SkillCreate(
            name=name,
            description=description,
            version=version,
            author=author,
            download_url=f"https://example.com/skills/{name}-{version}.zip",
        )
        created = crud.create_skill(db, skill)
        if random.random() > 0.3:
            crud.increment_skill_installed_count(db, created.id)
    print("默认技能创建完成")


if __name__ == "__main__":
    init_default_instances()
    print("数据初始化完成")
