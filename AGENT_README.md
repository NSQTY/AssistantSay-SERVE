# AGENT_README（Agent 操作手册）

> 读者：**以开发/运维身份工作的 Agent**。告诉你怎么使用本系统、开发外部插件、协助开发校验库，以及绝对不能碰的红线。
> 细节深文档不在此重复，一律**单向引用**各仓库根 README（唯一知识源）：SERVE（本目录 README.md）/ [AssistantSay-FunctionTools](https://github.com/NSQTY/AssistantSay-FunctionTools) / [AssistantSay-VerificationLibrary](https://github.com/NSQTY/AssistantSay-VerificationLibrary)。

## 1. 角色（先认清你是谁）

| 角色 | 定义 | 对 SERVE 的权限 | Agent 对应场景 |
|---|---|---|---|
| 消费者 | Clone 下来运行/使用 | 只读/运行 | 只调 API 用系统 |
| **第三方开发者** | Clone 下来自己开发插件 | **零文件接触**（连 init/copy 都禁止），只能 Workspace API | **Agent 默认角色** |
| 官方 | SERVE 仓库维护者 | 唯一有装配权 | 受官方指示时（帮官方装配/开发 VL 分支） |

**判定规则**：没有 SERVE 装配权 = 第三方。第三方时：你的插件留在你自己的目录，SERVE 只通过 API 见你。

## 2. 系统怎么用（消费者/第三方通用）

- 一切皆 API：`GET /` 看入口清单 → `GET /Documentation/get_blueprints`（蓝图=插件）→ `POST /Documentation/get_blueprint_routes`（函数=API）→ GET 函数 = 契约+信息（信封 `{"result": ...}`，错误 `{"error": ...}`）
- 页面型 API 的类型靠**响应自证**：GET 返回 HTML = 页面；JSON = 契约（含 V2 信息保留键 `蓝图信息`/`api信息`/`自定义信息`）
- 重载唯一入口：`POST /overload?reason=原因`（0.5s 后重启；改插件/登记后必须重载生效）
- 装配生效时序：登记/装配 → `POST /overload` → 重启后 LoadAllWorks 启动时装配

## 3. 如何开发外部插件（第三方 Agent 标准动作）

插件留在你自己的目录，SERVE 只通过 API 见你。目录结构（最小）：

```
MyPlugin/
├── README.md      ← 头部「能力定位」+ API 说明 + 尾部「## 依赖声明」
└── plugin.py      ← 蓝图模块（模块级建蓝图）
```

### 3.1 API 型插件（现在就能用 · 完整示例）

`plugin.py`：
```python
"""MyPlugin: API 型外部插件示例(校验器: 基座 FunctionHandler)"""
import System
from typing import Annotated

# 蓝图即属性: 名字合一(蓝图名 == url_prefix); 禁写根路由; 路径 = 函数名
Tools = System.FlaskApp.AR.CBP.MyPlugin.ModifyConfiguration(url_prefix='/MyPlugin')

@Tools.route('/Hello', methods=['POST', 'GET'])
@System.RouteInterception.CheckRequester()
def Hello(name: Annotated[str, '名字(必填)'], times: Annotated[int, '重复次数, 默认 1'] = 1) -> Annotated[dict, '问候结果']:
    '''简单问候 API: POST 才执行, GET 返回契约'''
    return {'greeting': ('你好 ' + name + '! ') * times}
```

`README.md`：
```markdown
# MyPlugin

## 能力定位
一句话：这个插件解决什么问题。

## API（统一信封）
| POST/GET | /MyPlugin/Hello | name: str 必填, times: int 默认1 | 问候结果 |

## 依赖声明
- 校验库版本：基座
```

登记（不 copy、不改 init）：
```
POST /Workspace/RegistrationWorks  {"WorksPath": "你的插件目录绝对路径", "Module": "plugin.py"}
POST /overload?reason=登记了MyPlugin        ← 生效(启动时自动装配)
```

### 3.2 页面型插件（前置：SERVE 已挂载官方页面分支）

页面 = GET 返回 HTML（浏览器直达；webui/Agent 靠响应自证识别）。校验器**只能从官方家族选**——现成页面分支 = VL 的 `AssistantSay_HANDLER_V1`（home 语义，冻结）；官方发布新页面分支后同样引用、依赖声明随之更新。

`plugin.py`：
```python
"""PagePlugin: 页面型外部插件示例(校验器: VL 页面分支, 官方挂载)"""
import System
from pathlib import Path
from VerificationLibrary.AssistantSay_HANDLER_V1 import Handler as PageHandler

Page = System.FlaskApp.AR.CBP.PagePlugin.ModifyConfiguration(
    url_prefix='/PagePlugin',
    static_folder=str(Path(__file__).resolve().parent / 'static'),   # 必须绝对路径(见 VL 契约)
)

@Page.route('/home', methods=['GET'])          # 禁写根路由: 命名路径即可
@System.RouteInterception.CheckRequester(handler=PageHandler())
def home(): ...
```

目录需含 `static/index.html`（页面内容）。README 尾部：
```markdown
## 依赖声明
- 校验库版本：AssistantSay_HANDLER_V1（页面分支）
```

### 3.3 信息自证（V2 信息型，可选升级）

想让 API 的 GET 自带「蓝图信息 / api信息 / 自定义信息」（webui 看板据此渲染）：
```python
from VerificationLibrary.AssistantSay_HANDLER_V2 import Handler as InfoHandler

Tools = System.FlaskApp.AR.CBP.MyPlugin.ModifyConfiguration(
    url_prefix='/MyPlugin',
    蓝图信息={'能力': '一句话能力'},              # 蓝图级: 挂蓝图一次, 全蓝图 API 自证
)
@Tools.route('/Hello', methods=['POST', 'GET'])
@System.RouteInterception.CheckRequester(handler=InfoHandler(
    api信息={'用途': '问候', '示例': '{"name":"张三"}'},
    自定义信息={'分组': '示例'},
))
def Hello(name: Annotated[str, '名字'], ...): ...
```
依赖声明写 `AssistantSay_HANDLER_V2`。信息键不参与 POST 白名单（骨架只认参数契约）。

## 4. 如何协助开发校验库（官方身份 Agent）

校验库 = VerificationLibrary 官方资产，**第三方只能选型、不能另造**。以官方身份开发时（受官方指示）：
- 分支 = VL 仓库文件夹，版本定调：文件夹名带版本（`AssistantSay_HANDLER_V2`），**发布后不可覆盖**，新版 = 新文件夹
- 三件套：`handler.py`（继承基座 FunctionHandler，纯净：不 import flask、不执行函数、不碰白名单）+ `README.md`（版本名/继承源/使用）+ `__init__.py`（再导出）
- 两轴模型：型轴 = GET 呈现（API 型 / 页面型）；策略轴 = 守门/身份/审计（正交，走 verify 或未来骨架钩子，不另开型）
- V2 信息型范式：初始化传参 `蓝图信息`/`api信息`/`自定义信息`，GET 随契约自证（保留键）
- 装配进 SERVE 是官方动作（挂 VerificationLibrary 分支，禁止急切再导出；由使用方显式引入）

## 5. 红线自查（动手前逐条过）

- [ ] 我没有修改 SERVE 下任何 .py（含 System/**）
- [ ] 我没有改 `FunctionTools/__init__.py`（第三方场景连这个也不碰）
- [ ] 我没有把任何插件 copy/clone 进 SERVE（第三方一律 Workspace API）
- [ ] 我没有在 SERVE 内创建任何新文件（运行时 `.reload.log`/插件自管 json 除外，且非我手写）
- [ ] 我没有直接 `from flask import ...`、没有深路径 `from System.Core.X import ...`
- [ ] 我没有自带校验器 / 没有绕过白名单 / 没有在 handler 里执行函数
- [ ] 我的插件遵守：能力定位(头) + 依赖声明(尾)、名字合一、路径=函数名、禁写根路由
- [ ] 登记/装配后我执行了 `POST /overload`，且只经重载生效
- [ ] 文档细节不一致时，以 GitHub 仓库根 README 为准（唯一源），发现文档过时请报告官方

## 6. 仓库导航（深文档单向引用）

| 想知道 | 去哪 |
|---|---|
| 骨架机制/启动/API 清单/依赖装配 | 本目录 `README.md` |
| 插件开发规范/官方 vs 第三方装配/红线 | FT 仓库根 README |
| Workspace 插件（第三方唯一通道） | FT 仓库 `Workspace/README.md` |
| webui 看板插件 | FT 仓库 `webui/README.md` |
| 校验库家族/两轴模型/版本定调/V2 | VL 仓库根 README |
| V2 信息型校验器 | VL 仓库 `AssistantSay_HANDLER_V2/README.md` |
