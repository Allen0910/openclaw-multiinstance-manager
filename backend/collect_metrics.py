#!/usr/bin/env python3
"""
OpenClaw实例监控数据采集脚本
自动采集本地OpenClaw实例的运行数据，写入数据库
"""
import os
import sys
import time
import json
import psutil
import requests
from datetime import datetime
from sqlalchemy.orm import Session

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import crud, schemas

def get_local_metrics():
    """获取本地系统监控数据"""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    
    # 获取网络流量
    net_io = psutil.net_io_counters()
    network_in = net_io.bytes_recv / 1024  # KB/s
    network_out = net_io.bytes_sent / 1024  # KB/s
    
    # 获取运行中的进程数
    task_count = len([p for p in psutil.process_iter() if 'openclaw' in p.name().lower()])
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "network_in": network_in,
        "network_out": network_out,
        "task_count": task_count,
        "version": "v1.0.0"
    }

def get_openclaw_status(api_url="http://localhost:8080/status", api_key=""):
    """获取OpenClaw实例状态"""
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"获取OpenClaw状态失败: {e}")
        return None

def collect_and_save(instance_id=1):
    """采集并保存数据"""
    db = SessionLocal()
    try:
        # 优先获取OpenClaw真实数据，没有则使用系统数据
        openclaw_data = get_openclaw_status()
        if openclaw_data:
            metrics_data = openclaw_data
        else:
            metrics_data = get_local_metrics()
        
        # 更新实例状态
        crud.update_instance_heartbeat(db, instance_id, metrics_data)
        
        # 保存监控指标
        metric = schemas.MetricCreate(
            instance_id=instance_id,
            cpu_usage=metrics_data["cpu_usage"],
            memory_usage=metrics_data["memory_usage"],
            disk_usage=metrics_data["disk_usage"],
            network_in=metrics_data["network_in"],
            network_out=metrics_data["network_out"],
            task_count=metrics_data["task_count"]
        )
        crud.create_metric(db, metric)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据采集成功: CPU={metrics_data['cpu_usage']}%, 内存={metrics_data['memory_usage']}%")
        
        # 检查告警阈值
        check_alerts(db, instance_id, metrics_data)
        
    except Exception as e:
        print(f"数据采集失败: {e}")
    finally:
        db.close()

def check_alerts(db: Session, instance_id: int, metrics: dict):
    """检查告警阈值"""
    thresholds = {
        "cpu": 90,
        "memory": 90,
        "disk": 90
    }
    
    alerts = []
    
    if metrics["cpu_usage"] >= thresholds["cpu"]:
        alerts.append({
            "level": "warning",
            "title": "CPU使用率过高",
            "content": f"CPU使用率已达{metrics['cpu_usage']}%，超过阈值{thresholds['cpu']}%"
        })
    
    if metrics["memory_usage"] >= thresholds["memory"]:
        alerts.append({
            "level": "warning",
            "title": "内存使用率过高",
            "content": f"内存使用率已达{metrics['memory_usage']}%，超过阈值{thresholds['memory']}%"
        })
    
    if metrics["disk_usage"] >= thresholds["disk"]:
        alerts.append({
            "level": "warning",
            "title": "磁盘空间不足",
            "content": f"磁盘使用率已达{metrics['disk_usage']}%，超过阈值{thresholds['disk']}%"
        })
    
    # 创建告警
    for alert_data in alerts:
        alert = schemas.AlertCreate(
            instance_id=instance_id,
            level=alert_data["level"],
            title=alert_data["title"],
            content=alert_data["content"]
        )
        crud.create_alert(db, alert)
        print(f"触发告警: {alert_data['title']}")

def run_forever(interval=60):
    """持续运行采集"""
    print("OpenClaw监控采集服务启动")
    print(f"采集间隔: {interval}秒")
    print("=" * 50)
    
    while True:
        collect_and_save()
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        collect_and_save()
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
        run_forever(interval)
