"""VerificationLibrary: 官方校验库挂载点(骨架内)

    ① 基座 FunctionHandler = API 型默认处理者, 在此再导出
    ② 官方处理者分支(V1 页面 / V2 信息型) 以文件夹形式**官方挂载**;
       禁止在 __init__ 急切再导出(顶层引用 System 会循环)——由使用方显式引入:
           from VerificationLibrary.AssistantSay_HANDLER_V1 import Handler as PageHandler
           from VerificationLibrary.AssistantSay_HANDLER_V2 import Handler as InfoHandler
    ③ 谁能改: 仅官方装配动作(挂载分支/调整再导出); 第三方零触碰, 只能从官方家族选型(不自造校验器)

    知识源 README(家族契约/两轴模型/版本定调): https://github.com/NSQTY/AssistantSay-VerificationLibrary/blob/main/README.md
    仓库(处理者分支代码):                     https://github.com/NSQTY/AssistantSay-VerificationLibrary
"""
from .handler import FunctionHandler

__all__ = ['FunctionHandler']
