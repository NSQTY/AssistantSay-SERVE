"""预定义处理依赖包: 对外只认 包名.类名(经 __init__ 再导出)

    包名 = 命名空间 | 文件名 = 内部实现(小写) | 类名 = 对外出口(驼峰)
    禁止使用 VerificationLibrary.VerificationLibrary.xxx 这类深路径。
    开发知识源(装配/分支契约/红线): https://github.com/NSQTY/AssistantSay-VerificationLibrary
"""
from .handler import FunctionHandler

__all__ = ['FunctionHandler']
