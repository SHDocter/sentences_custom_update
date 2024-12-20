from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg, ArgStr
from configs.path_config import DATA_PATH

import os
import json
import datetime

__zx_plugin_name__ = "画饼"
__plugin_usage__ = """
usage：
    不知道你更爱吃开发组画的饼还是自己给开发组画饼（bushi
    指令：
        开炉
        画饼 馅料
        出炉
""".strip()
__plugin_des__ = "谁不爱画饼呢（"
__plugin_cmd__ = ["画饼", "开炉"]
__plugin_version__ = 0.4
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["画饼", "开炉"],
}

cmd = on_command("画饼", priority=5, block=True)
check_cmd = on_command("开炉", priority=5, block=True)
del_cmd = on_command("出炉", priority=5, block=True)

ScuDataPath = DATA_PATH / "scu"
CakePath = ScuDataPath / "cake.json"

if not ScuDataPath.exists():
    os.mkdir(ScuDataPath)

if not os.path.exists(CakePath):
    with open(CakePath, "w", encoding="utf-8") as f:
        f.write(r"{}")

@cmd.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 1:
        await cmd.finish("请输入馅料!")
    else:
        with open(CakePath, "r", encoding="utf-8") as f:
            CakeData = json.loads(f.read())
        cake = {"group_id": f"{event.group_id}",
"author": f"{event.sender.nickname}",
"time": f"{datetime.datetime.now().strftime('%Y%m%d')}",
"msg": f"{msg[0]}"
}
        CakeData.append(cake)
        with open(CakePath, "w", encoding="utf-8") as f:
            json.dump(CakeData, f, ensure_ascii=False, indent=4)
        await cmd.finish("新饼进炉辣!")

@check_cmd.handle()
async def _():
    with open(CakePath, "r", encoding="utf-8") as f:
        CakeData = json.loads(f.read())
    cake = []
    number = 0
    for data in CakeData:
        number += 1
        cake.append(f"{number} | {data['msg']} | {data['author']} | {data['time']}")
    cake = str(cake).replace("'", "").replace("[", "").replace("]", "").replace(", ", "\n").replace("\"", "")
    await check_cmd.finish(f"""饼：{len(CakeData)}

{cake}""")

@del_cmd.handle()
async def _(arg: Message = CommandArg()):
    flag = arg.extract_plain_text().strip().split()
    with open(CakePath, "r", encoding="utf-8") as f:
        CakeData = json.loads(f.read())
    del_cake = CakeData.pop(int(flag[0]) - 1)
    with open(CakePath, "w", encoding="utf-8") as f:
        json.dump(CakeData, f, ensure_ascii=False, indent=4)
    await del_cmd.finish(f"{dict(del_cake)['msg']} | 已出炉！")