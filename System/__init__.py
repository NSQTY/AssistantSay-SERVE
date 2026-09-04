"""系统总门面: 最顶层包 import 一切(第三方依赖 + 内部模块), 其余文件只 import System

使用范式:
    import System                              # 唯一导入
    System.jsonify / System.request            # 第三方依赖(从门面取, 禁止到处 from flask import)
    System.flask.Blueprint                     # 或走模块对象
    System.VerificationLibrary.FunctionHandler
    System.RouteInterception.CheckRequester
    System.FlaskApp.AR / System.FlaskApp.RegisterBlueprints

导入顺序(依赖序, 不可乱):
    flask(第三方, 最先) → VerificationLibrary(纯净) → FlaskApp(叶) → RouteInterception → Documentation
    保证任何内部模块 top-level 用 System.X 时绑定已就位。

规则:
    ① 第三方依赖只在本文件 import, 其余文件不得直接 import flask 等
    ② 外部/内部文件一律 import System, 禁止深路径 from System.Core.X import ...
    ③ stdlib(inspect/typing/pathlib 等)属内置, 可各自直接 import
"""

# ---- 0. 第三方依赖(统一集中于此) ----
import flask
from flask import Flask, Blueprint, jsonify, request

# ---- 1. 外部依赖(纯净) ----
import VerificationLibrary

# ---- 2. 核心模块(按依赖序逐个绑定) ----
from .Core import FlaskApp
from .Core import RouteInterception
from .Core import Documentation
# ---- 2.5 工具蓝图包(根目录平级, 绝对导入; 依赖 AR/CheckRequester → 排在核心之后) ----
import FunctionTools

# ---- 3. 常用扁平出口 ----
from .Core.FlaskApp import AR, RegisterBlueprints, HY_ApplicationRegistration, BluePrintObject

__all__ = ['flask', 'Flask', 'Blueprint', 'jsonify', 'request',
           'FlaskApp', 'RouteInterception', 'Documentation',
           'VerificationLibrary', 'AR', 'RegisterBlueprints',
           'HY_ApplicationRegistration', 'BluePrintObject']
