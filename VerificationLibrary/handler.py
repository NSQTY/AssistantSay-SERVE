"""预定义处理依赖: FunctionHandler 决定被装饰函数如何响应 GET/POST(最轻版)

    GET_dispatch  → GET 契约如何呈现(骨架装饰时已解析好契约, 传入)
    POST_dispatch → POST 校验 + 参数加工, 返回可执行参数(执行由骨架硬做)

    依赖纯净: 不碰 jsonify, 不执行函数; verify 是唯一扩展点(可子类重写)。
    1、这个包是用来定义校验库的，而FunctionHandler只能是由你开发的子类来扩展。
"""


class FunctionHandler:
    """函数处理器: 每个被 @CheckRequester(handler=...) 装饰的函数的请求处理者"""

    # ---------- GET: 契约呈现(可重写, 如返回 HTML 页面) ----------

    def GET_dispatch(self, request, contract: dict, func):
        """GET: 默认原样返回契约; 子类可重写(如返回 HTML 内容)"""
        return contract

    # ---------- GET: 呈现方式(基座保证 jsonify; 子类可重写为裸 HTML 等) ----------

    def GET_render(self, request, data):
        """GET 呈现: 基座保证 jsonify 信封; 想要裸 HTML/文件等, 子类重写此方法

        运行时惰性取 System(基座被门面先 import, 顶层取会循环)
        """
        import System
        return System.jsonify({'result': data})

    # ---------- POST: 校验 + 参数加工(过滤在骨架强制, 这里不负责白名单) ----------

    def POST_dispatch(self, request, contract: dict, func):
        """POST: 校验 + 返回候选参数(白名单过滤由骨架强制执行, 不可被重写绕过)"""
        data = request.get_json() or {}
        self.verify(data, contract)
        return data

    # ---------- POST: 执行后(尾钩子, 可重写) ----------

    def POST_result(self, request, params: dict, result):
        """POST 执行后: 结果加工 + 自定义信息(默认原样; 子类可附加 meta/warnings 等)"""
        return result

    # ---------- 中间策略(唯一扩展点, 可子类重写) ----------

    def verify(self, data: dict, contract: dict):
        """默认无操作; Agent 级处理者在此加身份/权限/业务策略"""
        pass
