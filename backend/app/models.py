from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from .database import Base
from datetime import datetime

class Instance(Base):
    """OpenClaw实例表"""
    __tablename__ = "instances"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, comment="实例名称")
    host = Column(String(100), comment="主机地址")
    port = Column(Integer, default=8080, comment="端口")
    api_key = Column(String(255), comment="API密钥")
    status = Column(String(20), default="offline", comment="状态: online/offline/error")
    version = Column(String(50), comment="版本号")
    cpu_usage = Column(Float, default=0.0, comment="CPU使用率")
    memory_usage = Column(Float, default=0.0, comment="内存使用率")
    disk_usage = Column(Float, default=0.0, comment="磁盘使用率")
    last_heartbeat = Column(DateTime, comment="最后心跳时间")
    group = Column(String(50), comment="分组")
    description = Column(Text, comment="描述")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Metric(Base):
    """监控指标表"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, index=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    network_in = Column(Float, default=0.0, comment="入站流量 KB/s")
    network_out = Column(Float, default=0.0, comment="出站流量 KB/s")
    task_count = Column(Integer, default=0, comment="运行中任务数")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, index=True)
    name = Column(String(100), comment="任务名称")
    type = Column(String(50), comment="任务类型: command/skill/upgrade")
    params = Column(JSON, comment="任务参数")
    status = Column(String(20), default="pending", comment="状态: pending/running/success/failed")
    result = Column(Text, comment="执行结果")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Skill(Base):
    """技能表"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    version = Column(String(50))
    author = Column(String(100))
    download_url = Column(String(255))
    installed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    """告警表"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, index=True)
    level = Column(String(20), comment="级别: info/warning/error/critical")
    title = Column(String(255), comment="告警标题")
    content = Column(Text, comment="告警内容")
    status = Column(String(20), default="unread", comment="状态: unread/resolved")
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    email = Column(String(100), unique=True, index=True)
    role = Column(String(20), default="user", comment="角色: admin/user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
