import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Timer
import System                      # 唯一导入: 第三方与内部都从 System 取

System.RegisterBlueprints(System.AR)                          # 统一注册(属性即蓝图, 幂等)

# ===== 重载控制: 唯一入口是 API, 不监听任何文件 =====
ROOT = Path(__file__).parent
RELOAD_LOG = ROOT / '.reload.log'               # 只做审计(不再是被监听文件)


@System.AR.route('/', methods=['GET'])
def index():
    # 根目录不提供能力信息, 只给系统入口清单(Agent 据此探路)
    return System.jsonify({'BasicRouting': [
        'GET /Documentation/get_blueprints',
        'GET /Documentation/get_blueprint_routes',
        'GET /overload',
    ]})


@System.AR.route('/overload', methods=['GET', 'POST'])
def overload():
    """系统重载唯一入口: GET = 契约(告知用法) / POST = 执行(审计 + 真实重启)

    不用 CheckRequester: 系统级控制端点, 对任何 Agent/开发者开放(强制约定: 只能经此重载)
    """
    if System.request.method == 'GET':
        # GET = 契约: 让 Agent 知道怎么重载
        return System.jsonify({
            'usage': '系统重载唯一入口',
            'action': 'POST /overload?reason=重载原因',
            'effect': '重启进程: 新插件/新代码/新规则生效',
            'audit': '原因记录于 .reload.log',
            'note': '重启后当前请求之后的连接会中断',
        })

    # POST = 执行: 审计落盘 + 响应先返回, 再真实重启
    reason = System.request.args.get('reason', 'manual')
    with open(RELOAD_LOG, 'a', encoding='utf-8') as f:
        f.write(f'{datetime.now().isoformat()} | {reason}\n')

    def restart():
        # Windows 上 os.execv 替换进程不可靠(端口/句柄残留, 新进程起不来):
        # 改为 起新进程 + 旧进程立即退出(退出即释放端口, 新进程 1~2s 后接管)
        subprocess.Popen([sys.executable] + sys.argv, close_fds=True)
        os._exit(0)

    Timer(0.5, restart).start()                 # 0.5s 后重启, 让 200 先送达
    return System.jsonify({'overload': 'triggered', 'reason': reason,
                           'effect': '0.5s 后重启'})


if __name__ == '__main__':
    # 不监听任何文件, 无自动重载: 重载唯一入口 = POST /overload
    System.AR.run(host='0.0.0.0', port=50001,
                  debug=True, use_reloader=False)
