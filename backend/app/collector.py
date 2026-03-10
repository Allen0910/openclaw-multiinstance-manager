import requests
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import crud, schemas
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstanceCollector:
    def __init__(self):
        self.db = SessionLocal()
    
    def collect_instance_metrics(self, instance):
        """采集单个实例的监控数据"""
        try:
            url = f"http://{instance.host}:{instance.port}/status"
            headers = {
                "Authorization": f"Bearer {instance.api_key}"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 更新实例状态
            crud.update_instance_heartbeat(self.db, instance.id, {
                "cpu_usage": data.get("cpu_usage", 0),
                "memory_usage": data.get("memory_usage", 0),
                "disk_usage": data.get("disk_usage", 0),
                "version": data.get("version", "")
            })
            
            # 保存监控指标
            metric = schemas.MetricCreate(
                instance_id=instance.id,
                cpu_usage=data.get("cpu_usage", 0),
                memory_usage=data.get("memory_usage", 0),
                disk_usage=data.get("disk_usage", 0),
                network_in=data.get("network_in", 0),
                network_out=data.get("network_out", 0),
                task_count=data.get("running_tasks", 0)
            )
            crud.create_metric(self.db, metric)
            
            logger.info(f"成功采集实例 {instance.name} 的监控数据")
            return True
            
        except Exception as e:
            logger.error(f"采集实例 {instance.name} 失败: {str(e)}")
            # 标记实例为离线
            crud.update_instance(self.db, instance.id, schemas.InstanceUpdate(status="offline"))
            return False
    
    def collect_all(self):
        """采集所有实例的监控数据"""
        instances = crud.get_instances(self.db)
        for instance in instances:
            self.collect_instance_metrics(instance)
    
    def run_forever(self, interval=60):
        """持续运行采集任务"""
        logger.info("监控采集服务启动")
        while True:
            try:
                self.collect_all()
            except Exception as e:
                logger.error(f"采集循环异常: {str(e)}")
            time.sleep(interval)

if __name__ == "__main__":
    collector = InstanceCollector()
    collector.run_forever()
