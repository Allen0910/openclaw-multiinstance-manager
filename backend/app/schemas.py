from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Instance
class InstanceBase(BaseModel):
    name: str
    host: str
    port: int = 8080
    group: Optional[str] = None
    description: Optional[str] = None


class InstanceCreate(InstanceBase):
    api_key: str


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    api_key: Optional[str] = None
    group: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class Instance(InstanceBase, ORMBaseModel):
    id: int
    status: str
    version: Optional[str] = None
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Metric
class MetricBase(BaseModel):
    instance_id: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in: float = 0.0
    network_out: float = 0.0
    task_count: int = 0


class MetricCreate(MetricBase):
    pass


class Metric(MetricBase, ORMBaseModel):
    id: int
    created_at: datetime


# Task
class TaskBase(BaseModel):
    instance_id: int
    name: str
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class Task(TaskBase, ORMBaseModel):
    id: int
    status: str
    result: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime


# Skill
class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: str
    author: Optional[str] = None
    download_url: str


class SkillCreate(SkillBase):
    pass


class Skill(SkillBase, ORMBaseModel):
    id: int
    installed_count: int
    created_at: datetime


class SkillInstallRequest(BaseModel):
    instance_id: Optional[int] = None


class SkillInstallResponse(BaseModel):
    message: str
    task_id: Optional[int] = None
    skill_id: int
    installed_count: int


# Alert
class AlertBase(BaseModel):
    instance_id: int
    level: str
    title: str
    content: str


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None


class Alert(AlertBase, ORMBaseModel):
    id: int
    status: str
    resolved_at: Optional[datetime] = None
    created_at: datetime


# User
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    password: str


class User(ORMBaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class CommandExecuteRequest(BaseModel):
    command: str
    instance_id: Optional[int] = None
    timeout: int = Field(default=20, ge=1, le=60)


class CommandExecuteResponse(BaseModel):
    command: str
    instance_id: Optional[int] = None
    instance_name: Optional[str] = None
    exit_code: int
    stdout: str
    stderr: str
    output: str
    executed_at: datetime


# Auth
class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
