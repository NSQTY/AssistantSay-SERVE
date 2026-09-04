import inspect
import System                      # 第三方依赖从门面取, 不直接 import flask


def RegisterBlueprints(app):
    """注册应用上所有已挂载且未注册的蓝图(属性即蓝图, 幂等); 同时强制名字合一校验"""
    for name in dir(app):
        bp = getattr(app, name)
        if isinstance(bp, System.Blueprint) and bp.name not in app.blueprints:
            if bp.url_prefix and bp.url_prefix != '/' + bp.name:
                raise TypeError(f'名字合一违例: 蓝图名 {bp.name} != url_prefix {bp.url_prefix}')
            app.register_blueprint(bp)


class BluePrintObject(System.flask.Blueprint):
    """带链式配置能力的蓝图: 配置方法返回自己, 且自身可当透传装饰器"""

    def ModifyConfiguration(self, **options):
        for key, value in options.items():
            existing = getattr(self, key, None)
            if callable(existing):              # 禁止覆盖蓝图已有的方法
                raise TypeError(f'禁止覆盖蓝图的方法: {key}')
            setattr(self, key, value)           # 普通属性: 同名即覆盖
        return self                             # 链式: 返回自己

    def __call__(self, func):                   # 装饰器用法: 透传函数
        return func


class HY_ApplicationRegistration(System.flask.Flask):
    """Flask 应用: 蓝图即属性, 每个实例自带 CBP 访问器"""

    class CreateBluePrint:
        """蓝图代理: 访问 CBP.xxx 即创建/获取名为 xxx 的蓝图, 挂到所属应用实例上"""

        def __init__(self, app=None):
            self.app = app

        def __getattr__(self, name):
            existing = getattr(self.app, name, None)   # 缓存: 已有蓝图直接返回
            if isinstance(existing, System.Blueprint):
                return existing
            bp = BluePrintObject(name, self.app.import_name)
            setattr(self.app, name, bp)                # 挂到应用实例上
            return bp

    def __init__(self, import_name=__name__):
        super().__init__(import_name)
        self.CBP = self.CreateBluePrint(self)          # 每个实例自带的访问器


AR = HY_ApplicationRegistration(__name__)
