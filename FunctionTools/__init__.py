"""FunctionTools: 官方插件装配层(骨架内, 显式登记制)

    每个官方插件在此一行登记(官方装配动作), 例如:
        from .Workspace import Registration
        from .webui import WEBUI
    本地装配差异**仅限登记行**; 其余内容任何人(含官方)不得改动。
    第三方零触碰 SERVE(连本文件都不能动), 只能经 Workspace API 外部化注册。

    知识源 README(插件契约/装配/红线): https://github.com/NSQTY/AssistantSay-FunctionTools/blob/main/README.md
    仓库(官方插件代码):               https://github.com/NSQTY/AssistantSay-FunctionTools
"""
