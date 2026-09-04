# AssistantSay-SERVE

## 定位
AssistantSay 的核心运行骨架，所有代码的最终汇聚点和运行态。插件（来自 AssistantSay-FunctionTools）和处理者（来自 AssistantSay-VerificationLibrary）最终都装配进此目录运行。

**未来方向**：SERVE 会越来越薄，只保留门面、闸门、重载、文档四个基础设施能力，业务逻辑全部外置。

---

## ⚠️ 铁律：禁止修改任何代码

**任何组织、个人、Agent 均不能修改 AssistantSay-SERVE/ 下的任何代码。**

原因：核心极薄且全部接口已通过 System 暴露，修改核心代码 = 破坏契约 = 无法运行。

允许的唯一改动：`__init__.py` 的登记行（加载外部插件）。

所有业务逻辑必须在外部开发，通过 clone + copy + 改 init 的方式装配。

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
