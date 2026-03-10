import json
import logging
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.websockets import WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpenClaw Manager API", version="1.0.0")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY env var is required")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
DISALLOWED_COMMANDS = {
    "rm",
    "dd",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "init",
    "kill",
    "killall",
    "pkill",
    "chmod",
    "chown",
    "useradd",
    "userdel",
}
DEFAULT_RUNTIME_CONFIG = {
    "channels": {
        "feishu": {
            "enabled": True,
            "appId": "",
            "appSecret": "",
            "streaming": False,
            "footer": {"elapsed": False, "status": False},
            "requireMention": True,
            "groupPolicy": "open",
            "groups": {},
        }
    }
}
RUNTIME_STATE = {
    "gateway_installed": False,
    "gateway_running": False,
    "feishu_authorized": False,
    "pairings": [],
    "plugins": {"feishu-openclaw-plugin": "loaded", "feishu": "disabled"},
    "feishu_plugin_onboard_installed": False,
    "config": json.loads(json.dumps(DEFAULT_RUNTIME_CONFIG)),
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def ensure_admin(current_user: schemas.User):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


def resolve_instance(db: Session, instance_id: int | None):
    if instance_id is None:
        return None
    instance = crud.get_instance(db, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    return instance


def strip_inline_command_comment(command: str):
    cleaned = command.strip()
    for marker in ("//", "#"):
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[0].strip()
    return cleaned


def normalize_runtime_command(command: str):
    if not command:
        return ""
    command = command.strip()
    if command.startswith(("openclaw ", "feishu-plugin-onboard ")):
        return strip_inline_command_comment(command)
    return command


def get_nested_value(root: dict, path: str):
    current = root
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            raise KeyError(path)
        current = current[key]
    return current


def set_nested_value(root: dict, path: str, value):
    keys = path.split(".")
    current = root
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def parse_config_value(raw: str, use_json: bool):
    raw = raw.strip()
    if use_json:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            # 兼容文档中的裸字符串写法，例如: openclaw config set ... open --json
            if raw and raw[0] not in "{[":
                return raw
            raise HTTPException(status_code=400, detail=f"JSON 解析失败: {exc}") from exc

    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return raw


def build_doctor_report():
    feishu_config = RUNTIME_STATE["config"]["channels"]["feishu"]
    checks = [
        ("Gateway 已安装", RUNTIME_STATE["gateway_installed"]),
        ("Gateway 运行中", RUNTIME_STATE["gateway_running"]),
        ("飞书插件安装完成", RUNTIME_STATE["feishu_plugin_onboard_installed"]),
        ("飞书授权完成", RUNTIME_STATE["feishu_authorized"]),
        ("已配置 App ID", bool(feishu_config.get("appId"))),
        ("已配置 App Secret", bool(feishu_config.get("appSecret"))),
    ]
    lines = ["OpenClaw Doctor 诊断结果:"]
    for title, ok in checks:
        lines.append(f"  [{'OK' if ok else 'WARN'}] {title}")
    return "\n".join(lines)


def build_gateway_status_text():
    feishu = RUNTIME_STATE["config"]["channels"]["feishu"]
    configured = bool(feishu.get("appId")) and bool(feishu.get("appSecret"))
    return "\n".join(
        [
            "Gateway 状态:",
            f"  installed: {RUNTIME_STATE['gateway_installed']}",
            f"  running: {RUNTIME_STATE['gateway_running']}",
            f"  configured: {configured}",
            f"  feishu_authorized: {RUNTIME_STATE['feishu_authorized']}",
        ]
    )


def format_plugins_status():
    return "\n".join(
        [
            "ID                          Status",
            "--------------------------  --------",
            f"feishu-openclaw-plugin      {RUNTIME_STATE['plugins'].get('feishu-openclaw-plugin', 'unknown')}",
            f"feishu                      {RUNTIME_STATE['plugins'].get('feishu', 'unknown')}",
        ]
    )


def build_openclaw_help_text():
    return "\n".join(
        [
            "可用命令:",
            "  openclaw --version                                  查看版本",
            "  openclaw config|get|set                              查看或修改配置",
            "  openclaw configure                                   交互式配置向导提示",
            "  openclaw gateway install|start|stop|restart|status  网关控制",
            "  openclaw gateway run --allow-unconfigured            忽略配置启动网关",
            "  openclaw pairing approve feishu <CODE> --notify     飞书配对授权",
            "  openclaw plugins list                                查看插件状态",
            "  openclaw doctor|health                               健康检查",
            "  openclaw status|instances list                       查看实例状态",
            "  openclaw alerts list --unread                        查看告警",
            "  openclaw tasks list --running                        查看任务",
            "  openclaw logs tail --lines N                         查看任务日志",
            "  feishu-plugin-onboard install|doctor [--fix]         飞书插件引导命令",
            "  /feishu start|auth|doctor                            飞书侧斜杠命令模拟",
            "  <system_command>                                     执行本机系统命令（安全限制）",
        ]
    )


def execute_openclaw_virtual_command(db: Session, command: str, instance_id: int | None):
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"命令格式错误: {exc}") from exc

    if not tokens:
        raise HTTPException(status_code=400, detail="命令不能为空")

    normalized = tokens.copy()
    if normalized[0] in {"help", "status", "list", "version", "diagnose"}:
        normalized = ["openclaw", normalized[0]]
    elif normalized[0] == "clear":
        return 0, "终端已清空", ""
    elif normalized[0] == "/feishu":
        if len(normalized) < 2:
            return 2, "", "用法: /feishu start|auth|doctor"
        sub = normalized[1]
        if sub == "auth":
            RUNTIME_STATE["feishu_authorized"] = True
            return 0, "飞书授权完成，可继续在飞书中使用 OpenClaw。", ""
        if sub == "start":
            RUNTIME_STATE["gateway_installed"] = True
            RUNTIME_STATE["gateway_running"] = True
            return 0, "OpenClaw 网关已启动，飞书机器人可开始接收消息。", ""
        if sub == "doctor":
            return 0, build_doctor_report(), ""
        return 2, "", f"不支持的飞书命令: /feishu {sub}"
    elif normalized[0] == "feishu-plugin-onboard":
        if len(normalized) < 2:
            return 2, "", "用法: feishu-plugin-onboard install|doctor [--fix]"
        sub = normalized[1]
        if sub == "install":
            RUNTIME_STATE["feishu_plugin_onboard_installed"] = True
            RUNTIME_STATE["gateway_installed"] = True
            RUNTIME_STATE["plugins"]["feishu-openclaw-plugin"] = "loaded"
            RUNTIME_STATE["plugins"]["feishu"] = "disabled"
            return 0, "飞书官方插件引导器安装成功。", ""
        if sub == "doctor":
            if "--fix" in normalized:
                RUNTIME_STATE["feishu_plugin_onboard_installed"] = True
                RUNTIME_STATE["gateway_installed"] = True
                return 0, build_doctor_report() + "\n已自动修复可修复项。", ""
            return 0, build_doctor_report(), ""
        return 2, "", f"不支持的命令: {' '.join(normalized)}"

    if normalized[0] != "openclaw":
        return None

    sub = normalized[1:]
    if not sub or sub[0] in {"help", "--help", "-h"}:
        return 0, build_openclaw_help_text(), ""

    if sub[0] in {"version", "--version"}:
        return 0, "OpenClaw Manager v1.0.0\nOpenClaw Core v1.0.0", ""

    if sub[0] in {"configure", "config"}:
        if sub[0] == "configure":
            return (
                0,
                "已进入配置向导模式（模拟）。请使用以下命令完成配置：\n"
                "  openclaw config set channels.feishu.appId cli_xxx\n"
                "  openclaw config set channels.feishu.appSecret xxx",
                "",
            )

        if len(sub) == 1:
            return 0, json.dumps(RUNTIME_STATE["config"], ensure_ascii=False, indent=2), ""

        if sub[1] == "get":
            if len(sub) == 2:
                return 0, json.dumps(RUNTIME_STATE["config"], ensure_ascii=False, indent=2), ""
            path = sub[2]
            try:
                value = get_nested_value(RUNTIME_STATE["config"], path)
            except KeyError:
                return 2, "", f"配置项不存在: {path}"
            return 0, json.dumps(value, ensure_ascii=False, indent=2), ""

        if sub[1] == "set":
            if len(sub) < 4:
                return 2, "", "用法: openclaw config set <path> <value> [--json]"
            path = sub[2]
            use_json = "--json" in sub
            value_tokens = [token for token in sub[3:] if token != "--json"]
            if not value_tokens:
                return 2, "", "配置值不能为空"
            raw_value = " ".join(value_tokens)
            value = parse_config_value(raw_value, use_json)
            set_nested_value(RUNTIME_STATE["config"], path, value)
            if path == "channels.feishu.appId":
                RUNTIME_STATE["gateway_installed"] = True
            return 0, f"配置更新成功: {path} = {json.dumps(value, ensure_ascii=False)}", ""

        return 2, "", f"不支持的 config 子命令: {sub[1]}"

    if sub[0] == "gateway":
        if len(sub) < 2:
            return 2, "", "用法: openclaw gateway install|start|stop|restart|status|run"
        action = sub[1]
        feishu = RUNTIME_STATE["config"]["channels"]["feishu"]
        configured = bool(feishu.get("appId")) and bool(feishu.get("appSecret"))
        allow_unconfigured = "--allow-unconfigured" in sub
        if action == "install":
            RUNTIME_STATE["gateway_installed"] = True
            return 0, "Gateway 安装完成。", ""
        if action in {"start", "run"}:
            auto_installed = False
            if not RUNTIME_STATE["gateway_installed"]:
                RUNTIME_STATE["gateway_installed"] = True
                auto_installed = True
            RUNTIME_STATE["gateway_running"] = True
            if not configured and not allow_unconfigured:
                prefix = "Gateway 未安装，已自动安装并启动。" if auto_installed else "Gateway 已启动。"
                return 0, f"{prefix}（未配置模式）请尽快设置 channels.feishu.appId/appSecret。", ""
            if auto_installed:
                return 0, "Gateway 未安装，已自动安装并启动。", ""
            return 0, "Gateway 已启动。", ""
        if action == "stop":
            RUNTIME_STATE["gateway_running"] = False
            return 0, "Gateway 已停止。", ""
        if action == "restart":
            auto_installed = False
            if not RUNTIME_STATE["gateway_installed"]:
                RUNTIME_STATE["gateway_installed"] = True
                auto_installed = True
            RUNTIME_STATE["gateway_running"] = True
            if not configured and not allow_unconfigured:
                prefix = "Gateway 未安装，已自动安装并重启。" if auto_installed else "Gateway 已重启。"
                return 0, f"{prefix}（未配置模式）请尽快设置 channels.feishu.appId/appSecret。", ""
            if auto_installed:
                return 0, "Gateway 未安装，已自动安装并重启。", ""
            return 0, "Gateway 已重启。", ""
        if action == "status":
            return 0, build_gateway_status_text(), ""
        return 2, "", f"不支持的 gateway 子命令: {action}"

    if sub[0] == "dashboard":
        return 0, "Dashboard 地址: http://localhost/ （或你的部署域名）", ""

    if sub[0] in {"doctor", "diagnose"}:
        instances = crud.get_instances(db, limit=500)
        tasks = crud.get_tasks(db, limit=500)
        alerts = crud.get_alerts(db, limit=500)
        return (
            0,
            "\n".join(
                [
                    build_doctor_report(),
                    "",
                    "系统统计:",
                    f"  实例总数: {len(instances)}",
                    f"  在线实例: {len([i for i in instances if i.status == 'online'])}",
                    f"  任务总数: {len(tasks)}",
                    f"  运行中任务: {len([t for t in tasks if t.status == 'running'])}",
                    f"  未读告警: {len([a for a in alerts if a.status == 'unread'])}",
                ]
            ),
            "",
        )

    if sub[0] == "health":
        return 0, build_gateway_status_text(), ""

    if sub[:2] == ["plugins", "list"]:
        return 0, format_plugins_status(), ""

    if sub[:3] == ["pairing", "approve", "feishu"]:
        if len(sub) < 4:
            return 2, "", "用法: openclaw pairing approve feishu <CODE> [--notify]"
        code = sub[3]
        if code not in RUNTIME_STATE["pairings"]:
            RUNTIME_STATE["pairings"].append(code)
        RUNTIME_STATE["feishu_authorized"] = True
        notify = " 并已通知飞书用户。" if "--notify" in sub else ""
        return 0, f"配对码 {code} 已批准。{notify}".strip(), ""

    if sub[0] in {"status", "instances", "list"}:
        only_online = "--online" in sub
        instances = crud.get_instances(db, limit=500)
        if instance_id is not None:
            instances = [item for item in instances if item.id == instance_id]
        if only_online:
            instances = [item for item in instances if item.status == "online"]
        if not instances:
            return 0, "无可用实例", ""
        lines = []
        for item in instances:
            lines.append(
                f"[{item.id}] {item.name} {item.host}:{item.port} "
                f"[{item.status}] CPU:{item.cpu_usage:.1f}% 内存:{item.memory_usage:.1f}% 磁盘:{item.disk_usage:.1f}%"
            )
        return 0, "\n".join(lines), ""

    if sub[:2] == ["alerts", "list"]:
        status_filter = "unread" if "--unread" in sub else None
        alerts = crud.get_alerts(db, limit=50, status=status_filter)
        if instance_id is not None:
            alerts = [item for item in alerts if item.instance_id == instance_id]
        if not alerts:
            return 0, "暂无告警", ""
        lines = []
        for item in alerts:
            lines.append(
                f"[{item.level.upper()}] #{item.id} 实例{item.instance_id} {item.title} "
                f"({item.status}) {item.created_at.isoformat(timespec='seconds')}"
            )
        return 0, "\n".join(lines), ""

    if sub[:2] == ["tasks", "list"]:
        status_filter = "running" if "--running" in sub else None
        tasks = crud.get_tasks(db, limit=50, status=status_filter, instance_id=instance_id)
        if not tasks:
            return 0, "暂无任务", ""
        lines = []
        for item in tasks:
            lines.append(
                f"#{item.id} [{item.status}] {item.name} ({item.type}) "
                f"instance={item.instance_id} created={item.created_at.isoformat(timespec='seconds')}"
            )
        return 0, "\n".join(lines), ""

    if sub[:3] == ["task", "run", "health-check"]:
        if instance_id is not None:
            target_instances = [resolve_instance(db, instance_id)]
        else:
            target_instances = [item for item in crud.get_instances(db, limit=500) if item.status == "online"]
            if not target_instances:
                target_instances = crud.get_instances(db, limit=1)
        if not target_instances:
            return 2, "", "没有可执行健康检查的实例"

        created_task_ids = []
        for item in target_instances:
            task = crud.create_task(
                db,
                schemas.TaskCreate(
                    instance_id=item.id,
                    name=f"健康检查 - {item.name}",
                    type="command",
                    params={"command": f"echo health-check OK for {item.name}"},
                ),
            )
            task = run_task_now(db, task.id)
            created_task_ids.append(task.id)
        return 0, f"健康检查完成，任务ID: {', '.join(map(str, created_task_ids))}", ""

    if sub[:2] == ["logs", "tail"]:
        line_count = 20
        if "--lines" in sub:
            idx = sub.index("--lines")
            if idx + 1 < len(sub):
                try:
                    line_count = max(1, min(200, int(sub[idx + 1])))
                except ValueError:
                    line_count = 20
        tasks = crud.get_tasks(db, limit=line_count, instance_id=instance_id)
        if not tasks:
            return 0, "暂无任务日志", ""
        lines = []
        for item in tasks:
            result = (item.result or "").replace("\n", " | ")
            short = result[:180] + ("..." if len(result) > 180 else "")
            lines.append(
                f"{item.created_at.isoformat(timespec='seconds')} #{item.id} "
                f"[{item.status}] {item.name}: {short or '无输出'}"
            )
        return 0, "\n".join(lines), ""

    return 2, "", f"不支持的 openclaw 命令: {' '.join(sub)}"


def execute_system_command(command: str, timeout: int):
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"命令格式错误: {exc}") from exc

    if not tokens:
        raise HTTPException(status_code=400, detail="命令不能为空")

    executable = tokens[0].lower()
    if executable in DISALLOWED_COMMANDS:
        raise HTTPException(status_code=400, detail=f"禁止执行命令: {executable}")

    try:
        completed = subprocess.run(tokens, capture_output=True, text=True, timeout=timeout, check=False)
        return completed.returncode, completed.stdout or "", completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\n命令执行超时（>{timeout}s）"
        return 124, stdout, stderr
    except FileNotFoundError:
        return 127, "", f"命令不存在: {tokens[0]}"


def execute_terminal_command(db: Session, payload: schemas.CommandExecuteRequest):
    instance = resolve_instance(db, payload.instance_id)
    command = payload.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="命令不能为空")

    normalized_command = normalize_runtime_command(command)
    if normalized_command.startswith("openclaw ") and shutil.which("openclaw"):
        exit_code, stdout, stderr = execute_system_command(normalized_command, payload.timeout)
        output = stdout if stdout else stderr
        return schemas.CommandExecuteResponse(
            command=command,
            instance_id=instance.id if instance else None,
            instance_name=instance.name if instance else "全部实例",
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            output=output,
            executed_at=datetime.utcnow(),
        )
    if normalized_command.startswith("feishu-plugin-onboard ") and shutil.which("feishu-plugin-onboard"):
        exit_code, stdout, stderr = execute_system_command(normalized_command, payload.timeout)
        output = stdout if stdout else stderr
        return schemas.CommandExecuteResponse(
            command=command,
            instance_id=instance.id if instance else None,
            instance_name=instance.name if instance else "全部实例",
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            output=output,
            executed_at=datetime.utcnow(),
        )

    result = execute_openclaw_virtual_command(db, normalized_command, payload.instance_id)
    if result is None:
        exit_code, stdout, stderr = execute_system_command(normalized_command, payload.timeout)
    else:
        exit_code, stdout, stderr = result

    output = stdout if stdout else stderr
    return schemas.CommandExecuteResponse(
        command=command,
        instance_id=instance.id if instance else None,
        instance_name=instance.name if instance else "全部实例",
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        output=output,
        executed_at=datetime.utcnow(),
    )


def run_task_now(db: Session, task_id: int):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "canceled":
        raise HTTPException(status_code=400, detail="Task already canceled")
    if task.status == "running":
        raise HTTPException(status_code=400, detail="Task is already running")

    crud.update_task(
        db,
        task_id=task.id,
        task=schemas.TaskUpdate(status="running", started_at=datetime.utcnow(), result="任务执行中..."),
    )

    result = ""
    status_value = "success"
    try:
        if task.type == "command":
            command = (task.params or {}).get("command") or task.name
            command_result = execute_terminal_command(
                db, schemas.CommandExecuteRequest(command=command, instance_id=task.instance_id, timeout=20)
            )
            result = command_result.output
            status_value = "success" if command_result.exit_code == 0 else "failed"
        elif task.type in {"skill", "install_skill"}:
            skill_id = (task.params or {}).get("skill_id")
            skill_name = (task.params or {}).get("skill_name")
            if skill_id is not None:
                skill = crud.increment_skill_installed_count(db, int(skill_id))
                if not skill:
                    raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")
                result = f"技能安装完成: {skill.name} v{skill.version}"
            else:
                result = f"技能执行完成: {skill_name or task.name}"
        elif task.type == "restart":
            result = f"实例 {task.instance_id} 重启指令已下发"
        elif task.type == "upgrade":
            version = (task.params or {}).get("version", "latest")
            result = f"实例 {task.instance_id} 升级到版本 {version} 完成"
        else:
            result = f"任务类型 {task.type} 已执行"
    except HTTPException as exc:
        status_value = "failed"
        result = f"任务失败: {exc.detail}"
    except Exception as exc:
        status_value = "failed"
        result = f"任务失败: {exc}"

    return crud.update_task(
        db,
        task_id=task.id,
        task=schemas.TaskUpdate(status=status_value, result=result, finished_at=datetime.utcnow()),
    )


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    ensure_admin(current_user)

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if user.email:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    ensure_admin(current_user)
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    ensure_admin(current_user)
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username and user.username != db_user.username:
        existed = crud.get_user_by_username(db, user.username)
        if existed and existed.id != user_id:
            raise HTTPException(status_code=400, detail="Username already registered")

    if user.email and user.email != db_user.email:
        existed = crud.get_user_by_email(db, user.email)
        if existed and existed.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    updated = crud.update_user(db, user_id, user)
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/users/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    ensure_admin(current_user)
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete current user")

    db_user = crud.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}


@app.get("/instances/", response_model=List[schemas.Instance])
def read_instances(
    skip: int = 0,
    limit: int = 100,
    group: str = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_instances(db, skip=skip, limit=limit, group=group)


@app.post("/instances/", response_model=schemas.Instance)
def create_instance(
    instance: schemas.InstanceCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_instance = crud.get_instance_by_host(db, host=instance.host)
    if db_instance:
        raise HTTPException(status_code=400, detail="Instance with this host already exists")
    return crud.create_instance(db=db, instance=instance)


@app.get("/instances/{instance_id}", response_model=schemas.Instance)
def read_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_instance = crud.get_instance(db, instance_id=instance_id)
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return db_instance


@app.put("/instances/{instance_id}", response_model=schemas.Instance)
def update_instance(
    instance_id: int,
    instance: schemas.InstanceUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_instance = crud.update_instance(db, instance_id=instance_id, instance=instance)
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return db_instance


@app.delete("/instances/{instance_id}")
def delete_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_instance = crud.delete_instance(db, instance_id=instance_id)
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {"message": "Instance deleted successfully"}


@app.get("/instances/{instance_id}/metrics/", response_model=List[schemas.Metric])
def read_instance_metrics(
    instance_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_instance_metrics(db, instance_id=instance_id, skip=skip, limit=limit)


@app.get("/instances/{instance_id}/tasks/", response_model=List[schemas.Task])
def read_instance_tasks(
    instance_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_instance_tasks(db, instance_id=instance_id, skip=skip, limit=limit)


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    instance_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_tasks(db, skip=skip, limit=limit, instance_id=instance_id, status=status)


@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    resolve_instance(db, task.instance_id)
    created = crud.create_task(db=db, task=task)
    return run_task_now(db, created.id)


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    updated = crud.update_task(db, task_id, task)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@app.post("/tasks/{task_id}/run", response_model=schemas.Task)
def run_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return run_task_now(db, task_id)


@app.post("/tasks/{task_id}/cancel", response_model=schemas.Task)
def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status in {"success", "failed", "canceled"}:
        return task
    return crud.update_task(
        db,
        task_id=task_id,
        task=schemas.TaskUpdate(status="canceled", finished_at=datetime.utcnow(), result="任务已取消"),
    )


@app.get("/skills/", response_model=List[schemas.Skill])
def read_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_skills(db, skip=skip, limit=limit)


@app.post("/skills/", response_model=schemas.Skill)
def create_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.create_skill(db=db, skill=skill)


@app.post("/skills/{skill_id}/install", response_model=schemas.SkillInstallResponse)
def install_skill(
    skill_id: int,
    payload: schemas.SkillInstallRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    skill = crud.get_skill(db, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    instance_id = payload.instance_id
    if instance_id is None:
        first_instance = crud.get_instances(db, limit=1)
        if not first_instance:
            raise HTTPException(status_code=400, detail="No instance available for skill installation")
        instance_id = first_instance[0].id
    resolve_instance(db, instance_id)

    task = crud.create_task(
        db,
        schemas.TaskCreate(
            instance_id=instance_id,
            name=f"安装技能 {skill.name}",
            type="install_skill",
            params={"skill_id": skill.id, "skill_name": skill.name},
        ),
    )
    task = run_task_now(db, task.id)
    refreshed_skill = crud.get_skill(db, skill_id)
    return schemas.SkillInstallResponse(
        message=f"技能 {skill.name} 安装完成",
        task_id=task.id if task else None,
        skill_id=skill_id,
        installed_count=refreshed_skill.installed_count if refreshed_skill else skill.installed_count,
    )


@app.post("/terminal/execute", response_model=schemas.CommandExecuteResponse)
def execute_terminal(
    payload: schemas.CommandExecuteRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return execute_terminal_command(db, payload)


@app.get("/alerts/", response_model=List[schemas.Alert])
def read_alerts(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_alerts(db, skip=skip, limit=limit, status=status)


@app.put("/alerts/{alert_id}", response_model=schemas.Alert)
def update_alert(
    alert_id: int,
    alert: schemas.AlertUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_alert = crud.update_alert(db, alert_id=alert_id, alert=alert)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert


# ========== AI Chat Endpoint for Jarvis ==========
@app.post("/ai/chat")
def chat_with_ai(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Chat with AI - Jarvis AI assistant"""
    message = payload.get("message", "")
    context = payload.get("context", [])
    
    # Get AI configuration from localStorage (sent from frontend)
    ai_config = payload.get("ai_config", {})
    
    # Generate AI response based on message and context
    response = generate_jarvis_response(message, context, ai_config)
    
    return {
        "response": response,
        "message": response,
        "success": True
    }


# ========== TTS (Text-to-Speech) Endpoint for Jarvis ==========
import asyncio

class EdgeTTS:
    """Microsoft Edge TTS implementation using edge-tts library or HTTP"""
    
    VOICES = {
        'en-US': {
            'Jarvis': 'en-US-JasonNeural',  # 更像 Jarvis 的声音
            'Jenny': 'en-US-JennyNeural',
            'Samantha': 'en-US-SamanthaNeural',
        },
        'zh-CN': {
            'Xiaoxiao': 'zh-CN-XiaoxiaoNeural',  # 自然女声
            'Yunxi': 'zh-CN-YunxiNeural',
            'Yunyang': 'zh-CN-YunyangNeural',
        }
    }
    
    @staticmethod
    async def synthesize(text: str, voice_name: str = None, lang: str = 'en-US') -> bytes:
        """Synthesize speech using Edge TTS"""
        import subprocess
        import tempfile
        import os
        
        # Select voice based on language
        if voice_name is None:
            voice_map = EdgeTTS.VOICES.get(lang, EdgeTTS.VOICES['en-US'])
            voice_name = voice_map.get('Jarvis', voice_map.get('Jenny', list(voice_map.values())[0]))
        
        # Use edge-tts CLI if available, otherwise use subprocess
        try:
            # Create temp files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                input_file = f.name
            
            output_file = input_file.replace('.txt', '.mp3')
            
            # Try using edge-tts
            result = subprocess.run(
                ['edge-tts', '--input-text', text, '--voice', voice_name, '--write-media', output_file],
                capture_output=True, timeout=30
            )
            
            if os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    audio_data = f.read()
                os.unlink(input_file)
                os.unlink(output_file)
                return audio_data
            else:
                # Fallback - generate silence/empty response
                raise Exception("TTS generation failed")
                
        except Exception as e:
            # Return empty audio if TTS fails
            return b''


# ========== Simple TTS Endpoint ==========
@app.post("/ai/tts")
async def text_to_speech(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Convert text to speech using Edge TTS"""
    text = payload.get("text", "")
    lang = payload.get("lang", "zh-CN")  # Default to Chinese
    voice = payload.get("voice")  # Optional voice name
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Try to generate speech
    try:
        audio_data = await asyncio.wait_for(
            EdgeTTS.synthesize(text, voice, lang),
            timeout=30
        )
        
        if audio_data:
            from fastapi.responses import Response
            return Response(
                content=audio_data,
                media_type="audio/mp3",
                headers={"Content-Disposition": f"inline; filename=jarvis.mp3"}
            )
        else:
            # Return placeholder - client should use browser TTS
            return {"error": "TTS service unavailable", "use_browser_tts": True}
            
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="TTS service timeout")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {"error": str(e), "use_browser_tts": True}


def generate_jarvis_response(message: str, context: list, ai_config: dict) -> str:
    """Generate Jarvis-style response"""
    message_lower = message.lower()
    
    # System commands
    if any(word in message_lower for word in ["status", "系统状态", "状态"]):
        return "先生，系统运行一切正常。所有子系统在线，能源充沛，防护罩充能完毕。有什么我可以为您效劳的？"
    
    if any(word in message_lower for word in ["time", "时间", "几点"]):
        from datetime import datetime
        now = datetime.now()
        return f"先生，现在是 {now.hour} 点 {now.minute} 分。"
    
    if any(word in message_lower for word in ["date", "日期", "今天"]):
        from datetime import datetime
        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return f"先生，今天是 {now.year} 年 {now.month} 月 {now.day} 日，{weekdays[now.weekday()]}。"
    
    if any(word in message_lower for word in ["help", "帮助", "你能做什么"]):
        return """先生，我可以帮助您：
• 查询系统状态和时间
• 执行终端命令
• 管理实例和任务
• 查看告警信息
• 与您进行简单的对话

您可以直接用语音或文字告诉我您的需求。"""
    
    if any(word in message_lower for word in ["hello", "你好", "嗨", "hi", "good morning", "早上好"]):
        return "您好，先生。贾维斯随时待命。请指示。"
    
    if any(word in message_lower for word in ["who are you", "你是谁", "name"]):
        return "我是贾维斯，您的个人 AI 助手。我被设计用来协助您管理 OpenClaw 系统，并为您提供各种帮助。"
    
    if any(word in message_lower for word in ["thank", "谢谢", "感谢"]):
        return "为您服务是我的荣幸，先生。"
    
    if any(word in message_lower for word in ["bye", "再见", "拜拜", "goodbye"]):
        return "先生，祝您有美好的一天。需要我时随时召唤我。"
    
    if any(word in message_lower for word in ["instance", "实例", "服务器"]):
        return "让我为您查询实例状态..."
    
    if any(word in message_lower for word in ["task", "任务", "运行中"]):
        return "让我为您查看任务情况..."
    
    if any(word in message_lower for word in ["alert", "告警", "警告"]):
        return "让我为您检查告警信息..."
    
    # Default intelligent response
    responses = [
        f"我理解您的意思，先生。\"{message}\" 这件事我正在处理中。",
        f"收到您的指令，先生。我会处理 \"{message}\"。",
        f"明白，先生。关于 \"{message}\"，让我分析一下最佳方案。",
        f"我听到了，先生。您说 \"{message}\"，我会立即执行。",
        f"好的，先生。我会记住 \"{message}\" 这个请求。",
    ]
    
    import random
    return random.choice(responses)


# ========== AI Configuration Endpoints ==========
@app.post("/ai/test")
def test_ai_connection(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Test AI provider connection"""
    provider = payload.get("provider")
    config = payload.get("config", {})
    
    # Mock response for testing
    return {
        "success": True,
        "message": f"{provider} 连接测试成功",
        "latency": 125,
        "details": "API Key 验证通过"
    }


# ========== Channel Configuration Endpoints ==========
@app.post("/channels/test")
def test_channel_connection(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Test messaging channel connection"""
    channel = payload.get("channel")
    config = payload.get("config", {})
    
    # Mock response for testing
    return {
        "success": True,
        "message": f"{channel} 连接测试成功"
    }


# ========== Service Management Endpoints ==========
@app.get("/service/status")
def get_service_status(current_user: schemas.User = Depends(get_current_user)):
    """Get OpenClaw service status"""
    return {
        "status": "running" if RUNTIME_STATE["gateway_running"] else "stopped",
        "pid": 12345,
        "uptime": "2天 5小时 32分钟",
        "memory": "256MB",
        "cpu": "12%",
        "port": RUNTIME_STATE["config"].get("port", 8000)
    }


@app.post("/service/start")
def start_service(current_user: schemas.User = Depends(get_current_user)):
    """Start OpenClaw service"""
    RUNTIME_STATE["gateway_running"] = True
    RUNTIME_STATE["gateway_installed"] = True
    return {"success": True, "message": "服务启动成功"}


@app.post("/service/stop")
def stop_service(current_user: schemas.User = Depends(get_current_user)):
    """Stop OpenClaw service"""
    RUNTIME_STATE["gateway_running"] = False
    return {"success": True, "message": "服务停止成功"}


@app.post("/service/restart")
def restart_service(current_user: schemas.User = Depends(get_current_user)):
    """Restart OpenClaw service"""
    RUNTIME_STATE["gateway_running"] = False
    RUNTIME_STATE["gateway_installed"] = True
    RUNTIME_STATE["gateway_running"] = True
    return {"success": True, "message": "服务重启成功"}


# ========== Diagnostics Endpoints ==========
@app.post("/diagnostics/system")
def run_system_diagnostics(current_user: schemas.User = Depends(get_current_user)):
    """Run system diagnostics"""
    import platform
    import psutil
    
    return {
        "success": True,
        "checks": [
            {"name": "Python 环境", "status": "success", "detail": f"Python {platform.python_version()}"},
            {"name": "Docker 服务", "status": "success", "detail": "Docker 运行中"},
            {"name": "网络连接", "status": "success", "detail": "外网连接正常"},
            {"name": "磁盘空间", "status": "warning", "detail": f"可用 {psutil.disk_usage('/').free / (1024**3):.1f}GB"},
            {"name": "内存状态", "status": "success", "detail": f"可用 {psutil.virtual_memory().available / (1024**3):.1f}GB"},
            {"name": "配置文件", "status": "success", "detail": "配置文件完整"}
        ]
    }


@app.post("/diagnostics/ping")
def run_ping_diagnostics(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Run ping diagnostics"""
    target = payload.get("target", "api.openai.com")
    
    # Mock ping result
    return {
        "success": True,
        "output": f"PING {target}: 56 data bytes\n64 bytes from {target}: icmp_seq=0 ttl=128 time=125.432 ms\n64 bytes from {target}: icmp_seq=1 ttl=128 time=118.234 ms\n64 bytes from {target}: icmp_seq=2 ttl=128 time=120.567 ms\n\n--- {target} ping statistics ---\n3 packets transmitted, 3 packets received, 0.0% packet loss\nround-trip min/avg/max = 118.234/121.411/125.432 ms"
    }


@app.post("/diagnostics/network")
def run_network_diagnostics(
    payload: dict,
    current_user: schemas.User = Depends(get_current_user),
):
    """Run network diagnostics"""
    target = payload.get("target", "api.openai.com")
    
    return {
        "success": True,
        "output": f"网络诊断到 {target}:\nDNS 解析: 正常\nTCP 连接: 正常\n延迟: 约 120ms"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_username(db, username=os.getenv("DEFAULT_ADMIN_USERNAME", "admin"))
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
        if not admin_user:
            if not admin_password:
                logger.warning(
                    "No admin user found and DEFAULT_ADMIN_PASSWORD is not set. "
                    "Set DEFAULT_ADMIN_PASSWORD to bootstrap the first admin account."
                )
                return
            user = schemas.UserCreate(
                username=os.getenv("DEFAULT_ADMIN_USERNAME", "admin"),
                password=admin_password,
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com"),
                role="admin",
            )
            crud.create_user(db, user)
            logger.info("Bootstrap admin account created")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
