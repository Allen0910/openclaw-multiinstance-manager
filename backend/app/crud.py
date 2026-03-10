from datetime import datetime

import bcrypt
from sqlalchemy.orm import Session

from . import models, schemas


def hash_password(password: str):
    # bcrypt automatically truncates passwords to 72 bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.model_dump(exclude_unset=True)
    password = update_data.pop("password", None)
    if password:
        db_user.password_hash = hash_password(password)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# Instance
def get_instance(db: Session, instance_id: int):
    return db.query(models.Instance).filter(models.Instance.id == instance_id).first()


def get_instance_by_host(db: Session, host: str):
    return db.query(models.Instance).filter(models.Instance.host == host).first()


def get_instances(db: Session, skip: int = 0, limit: int = 100, group: str = None):
    query = db.query(models.Instance)
    if group:
        query = query.filter(models.Instance.group == group)
    return query.offset(skip).limit(limit).all()


def create_instance(db: Session, instance: schemas.InstanceCreate):
    db_instance = models.Instance(**instance.model_dump())
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return db_instance


def update_instance(db: Session, instance_id: int, instance: schemas.InstanceUpdate):
    db_instance = get_instance(db, instance_id)
    if db_instance:
        update_data = instance.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instance, key, value)
        db_instance.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_instance)
    return db_instance


def update_instance_heartbeat(db: Session, instance_id: int, metrics: dict):
    db_instance = get_instance(db, instance_id)
    if db_instance:
        db_instance.status = "online"
        db_instance.cpu_usage = metrics.get("cpu_usage", 0)
        db_instance.memory_usage = metrics.get("memory_usage", 0)
        db_instance.disk_usage = metrics.get("disk_usage", 0)
        db_instance.version = metrics.get("version", "")
        db_instance.last_heartbeat = datetime.utcnow()
        db.commit()
    return db_instance


def delete_instance(db: Session, instance_id: int):
    db_instance = get_instance(db, instance_id)
    if db_instance:
        db.delete(db_instance)
        db.commit()
    return db_instance


# Metric
def create_metric(db: Session, metric: schemas.MetricCreate):
    db_metric = models.Metric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


def get_instance_metrics(db: Session, instance_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Metric)
        .filter(models.Metric.instance_id == instance_id)
        .order_by(models.Metric.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# Task
def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100, instance_id: int = None, status: str = None):
    query = db.query(models.Task)
    if instance_id is not None:
        query = query.filter(models.Task.instance_id == instance_id)
    if status:
        query = query.filter(models.Task.status == status)
    return query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()


def get_instance_tasks(db: Session, instance_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Task)
        .filter(models.Task.instance_id == instance_id)
        .order_by(models.Task.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if db_task:
        update_data = task.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task


# Skill
def create_skill(db: Session, skill: schemas.SkillCreate):
    db_skill = models.Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def get_skills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Skill).offset(skip).limit(limit).all()


def get_skill(db: Session, skill_id: int):
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()


def increment_skill_installed_count(db: Session, skill_id: int):
    db_skill = get_skill(db, skill_id)
    if not db_skill:
        return None
    db_skill.installed_count = (db_skill.installed_count or 0) + 1
    db.commit()
    db.refresh(db_skill)
    return db_skill


# Alert
def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alerts(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.Alert)
    if status:
        query = query.filter(models.Alert.status == status)
    return query.order_by(models.Alert.created_at.desc()).offset(skip).limit(limit).all()


def update_alert(db: Session, alert_id: int, alert: schemas.AlertUpdate):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if db_alert:
        update_data = alert.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_alert, key, value)
        db.commit()
        db.refresh(db_alert)
    return db_alert
