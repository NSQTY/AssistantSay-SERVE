import System                      # 统一门面: 第三方(Blueprint)与内部都从 System 取
from typing import Annotated

AR = System.FlaskApp.AR
CheckRequester = System.RouteInterception.CheckRequester
FunctionHandler = System.VerificationLibrary.FunctionHandler
Blueprint = System.Blueprint

# 名字合一: 蓝图名(属性) == 注册名 == url_prefix
Documentation = AR.CBP.Documentation.ModifyConfiguration(url_prefix='/Documentation')


@AR.Documentation.route('/get_blueprints', methods=['POST', 'GET'])
def get_blueprints() -> Annotated[dict, '所有蓝图实例的清单(蓝图名 -> 描述)']:
    '''这个api是将所有蓝图实例展现出来'''
    blueprints = AR.blueprints
    return {k: f'<Blueprint: {v.name}>' for k, v in blueprints.items()}


@AR.Documentation.route('/get_blueprint_routes', methods=['GET', 'POST'])
@CheckRequester(handler=FunctionHandler())
def get_blueprint_routes(blueprint_name: Annotated[str, '要查询的蓝图名称'] = None) -> Annotated[dict, '蓝图 -> 函数名列表']:
    """返回蓝图下的函数名列表; 存不存在由 Agent 阅读结果自行判断"""
    blueprints = {k: v for k, v in AR.__dict__.items() if isinstance(v, Blueprint)}
    funcs = {name: sorted(fn.__name__ for ep, fn in AR.view_functions.items()
                          if ep.startswith(bp.name + '.'))
             for name, bp in blueprints.items()}
    return funcs.get(blueprint_name) if blueprint_name else funcs
