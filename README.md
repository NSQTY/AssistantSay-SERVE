# AssistantSay-SERVE

## 定位
AssistantSay 的核心运行骨架，所有代码的最终汇聚点和运行态。插件（来自 AssistantSay-FunctionTools）和处理者（来自 AssistantSay-VerificationLibrary）最终都装配进此目录运行。

**未来方向**：SERVE 会越来越薄，只保留门面、闸门、重载、文档四个基础设施能力，业务逻辑全部外置。

**能力分层**（SERVE 用来做什么）：
- **门面层**：`System` 统一门面（第三方依赖只在此 import）——结构保证，防深路径/循环导入
- **闸门层**：`@CheckRequester`（签名即契约 / 白名单强制过滤 / 骨架硬执行 / 统一信封）——调用方不可信时，骨架是契约的执行者
- **装配层**：插件/处理者文件夹进挂点 + 登记 + `POST /overload`——业务外置，核心极薄且不变
- **发现层**：`GET /` 与 `/Documentation/*`——Agent 仅凭 HTTP 发现与调用系统能力
- **重载层**：`POST /overload` + 审计落盘（无文件监听）——装配后生效的唯一入口

**不做什么**：不装业务逻辑、不代 Agent 决策、不碰文件系统——SERVE 是信使与契约执行者，不是业务大脑。

---

## ⚠️ 铁律与角色权限

### 铁律（所有人）
**任何组织、个人、Agent 均不能修改 AssistantSay-SERVE/ 下的任何代码。**

原因：核心极薄且全部接口已通过 System 暴露，修改核心代码 = 破坏契约 = 无法运行。

### 角色权限（分层）

| 角色 | 定义 | 对 SERVE 的权限 |
|---|---|---|
| **消费者** | Clone 下来运行/使用系统的人 | 只读/运行，零修改 |
| **第三方开发者（含 Agent）** | Clone 下来自己开发插件的人 | **零文件接触**：连 `__init__` 都不能动、连 copy 进 SERVE 都不允许；插件留自己目录，**只能经 Workspace API 外部化注册** |
| **官方** | SERVE 仓库维护者（AssistantSay 官方） | 唯一有装配权（官方插件 init 登记 / copy 装配 / 挂载 VL 分支）；也不改业务代码 |

> 业务逻辑一律外部化。**第三方装配唯一通道 = Workspace API**（登记 → 预注册导入测试 → 重载生效）；官方插件的 copy+init 装配是官方动作，第三方执行官方给出的安装步骤不算私自修改。

---

## 依赖与首次装配（clone 后必读）

**SERVE 骨架仓不含任何插件**（`FunctionTools/` 为空）。系统对第三方的外部化注册依赖 **Workspace 官方插件**——**clone 后必须执行官方装配动作拉取一个 Workspace 版本**，否则第三方通道缺位、无法注册任何插件。

**依赖能力要求（文字定调）**：Workspace 必须具备 ① README 必备校验 ② 预注册模块导入测试 ③ 蓝图名回填（blueprint_names）三项能力（FT 仓库当前版本已具备）。

**首次装配步骤（官方动作）**：
```powershell
cd your_path/AssistantSay-SERVE/FunctionTools
git clone https://github.com/NSQTY/AssistantSay-FunctionTools.git %TEMP%\ft
Copy-Item -Recurse %TEMP%\ft\Workspace .
# 在 FunctionTools/__init__.py 加登记行(官方动作):
#     from .Workspace import Registration
Remove-Item -Recurse %TEMP%\ft
python app.py            # 启动
POST /overload?reason=装配Workspace   # 如需热生效
```
> 此后：第三方注册外部插件 = `POST /Workspace/RegistrationWorks`（详见 FT 仓库根 README「第三方外部注册」）；官方插件（如 webui）继续走官方装配。

---

## 四个核心机制

### 1. 门面依赖机制
所有模块统一 `import System`，禁止直接 `from flask import ...`。
第三方依赖只在 `System/__init__.py` 集中 import，其余文件通过 `System.X` 取用。

**导入顺序（依赖序，不可乱）**：
flask → VerificationLibrary → FlaskApp → RouteInterception → Documentation → FunctionTools

### 2. 蓝图装配机制
- `AR`（HY_ApplicationRegistration 实例）：蓝图即属性，`AR.CBP.<名>` 懒创建并缓存
- `RegisterBlueprints(AR)`：遍历 `dir(app)`，幂等注册所有 Blueprint 实例
- **蓝图缓存**：同一个名字第二次访问不会覆盖已有蓝图，改配置必须重载

### 3. 请求闸门机制（@CheckRequester）
- GET：`GET_dispatch` 返回契约 → `GET_render` 呈现（默认 jsonify）
- POST：`POST_dispatch` 校验 + 加工 → **骨架强制白名单过滤** → `func(**params)` 硬执行 → `POST_result` 加工 → 统一信封 `{"result": ...}`
- 异常唯一通道：`{"error": str(e)}`
- **白名单过滤由骨架强制执行，handler 不可绕过**

### 4. 重载机制
- 唯一入口：`POST /overload?reason=X`
- 审计落盘：原因记录于 `.reload.log`（纯记录，不被监听，只追加不截断）
- 0.5s 后 `os.execv` 替换进程，重启生效
- **无文件监听**，Flask `use_reloader=False`

---

## 启动与系统 API

```bash
python app.py  →  监听 0.0.0.0:50001
```

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/` | 基础路由清单 |
| GET | `/overload` | 重载契约说明 |
| POST | `/overload?reason=X` | 触发重载（审计 + 0.5s 后重启） |
| GET | `/Documentation/get_blueprints` | 所有蓝图实例清单 |
| GET | `/Documentation/get_blueprint_routes?blueprint_name=X` | 蓝图 → 函数名映射（不存在返回 None） |

---

## 三文件夹结构

```
SERVE/
├── System/               门面 + 核心模块
│   ├── __init__.py       统一门面（依赖序：flask→VerificationLibrary→FlaskApp→RouteInterception→Documentation→FunctionTools）
│   └── Core/
│       ├── FlaskApp.py       AR / RegisterBlueprints / BluePrintObject
│       ├── RouteInterception.py  @CheckRequester 闸门
│       └── Documentation.py  系统级文档 API
├── FunctionTools/        插件装配挂点
└── VerificationLibrary/  处理者装配挂点
```

---

## 红线与禁止事项

| 禁止项 | 原因 |
|---|---|
| **修改 SERVE 下任何 .py 文件** | 核心契约，改代码 = 破坏运行 |
| **在 SERVE 内部创建新文件** | 除 `.reload.log` 由系统自动写外，禁止创建 |
| 删除 System/、FunctionTools/、VerificationLibrary/ 三个文件夹 | 骨架解体，系统无法运行 |
| 直接 `from flask import ...` | 破坏门面依赖隔离 |
| 深路径 `from System.Core.X import ...` | 破坏导入序，可能导致循环导入或 AttributeError |
| 修改导入顺序 | 内部模块 top-level 用 System.X 时绑定未就位 |
| 试图绕过白名单过滤 | 骨架强制执行，handler 不可覆盖 |
| 在 handler 中 import flask/jsonify | 破坏纯净原则，handler 不得碰第三方依赖 |
| 在 handler 中执行函数 | 执行权在骨架，handler 不得代劳 |
| 期望文件监听自动重载 | 系统无文件监听，唯一入口是 POST /overload |
| 启动后注册新蓝图 | Flask 第一次请求后冻结，外化蓝图必须在启动时加载 |
| 运维：不清理 .reload.log | 日志只追加不截断，长期运行会无限增长 |

---

## 仓库边界与文档去向

本 GitHub 仓库只含运行骨架；`FunctionTools/` 与 `VerificationLibrary/` 挂点内的插件/处理者内容不属于本仓库，来自下方两个独立仓库（以文件夹为单位 clone/copy 进挂点，登记 + `POST /overload` 后生效）。

- [AssistantSay-FunctionTools](https://github.com/NSQTY/AssistantSay-FunctionTools) — 官方插件库（开发知识源：仓库根 README）
- [AssistantSay-VerificationLibrary](https://github.com/NSQTY/AssistantSay-VerificationLibrary) — 官方校验库（开发知识源：仓库根 README）
