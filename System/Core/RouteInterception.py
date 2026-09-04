from functools import wraps
from typing import get_origin, get_args, Annotated
import inspect
import System                      # 统一门面: 第三方(jsonify/request)与内部都从 System 取


def _parse_contract(func) -> dict:
    """Annotated 解析: 装饰时建立契约(签名即契约, 初始化即强制成立)"""
    hints = inspect.getfullargspec(func).annotations
    contract = {}
    for name, hint in hints.items():
        if get_origin(hint) is Annotated:
            args = get_args(hint)
            contract[name] = {'type': args[0].__name__, 'description': args[1:]}
        elif hint is not inspect.Parameter.empty and name != 'return':
            # 裸注解: 类型给类名; 字符串注解(前向引用/偷懒写法)给原样
            type_name = hint.__name__ if isinstance(hint, type) else str(hint)
            contract[name] = {'type': type_name, 'description': ['(无描述)']}
    return contract


def CheckRequester(handler: 'System.VerificationLibrary.FunctionHandler' = None):
    """骨架: 拦截 + GET/POST 分调 + 硬执行

    GET  → handler.GET_dispatch(request, contract, func)  契约装饰时解析好, 不执行函数
    POST → handler.POST_dispatch → 白名单强制 → func(**params) 硬执行 → POST_result
    成功/失败统一信封: {"result": ...} / {"error": ...}
    """
    handler: 'System.VerificationLibrary.FunctionHandler' = handler or System.VerificationLibrary.FunctionHandler()

    def decorator(func):
        contract = _parse_contract(func)          # ① 装饰时: 契约初始化建立

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if System.request.method == 'GET':
                    data = handler.GET_dispatch(System.request, contract, func)  # ① 得数据
                    return handler.GET_render(System.request, data)              # ② 交给 handler 呈现(jsonify 或裸)
                params = handler.POST_dispatch(System.request, contract, func)      # 前: 库校验+加工(可重写)
                params = {k: v for k, v in params.items() if k in contract}  # 强制白名单: 执行前最后一道, 不可绕
                result = func(**params)                                      # 执行: 骨架硬执行
                data = handler.POST_result(System.request, params, result)   # 尾: 库加工结果
                return System.jsonify({'result': data})
            except Exception as e:
                return System.jsonify({'error': str(e)})           # 异常即唯一错误通道
        return wrapper
    return decorator
