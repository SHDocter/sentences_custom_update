from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.http_utils import AsyncHttpx


__zx_plugin_name__ = "羽月语录"
__plugin_usage__ = """
usage：
    羽月语录
    指令：
        羽月语录
        羽月语录十连
        羽月语录 ["查询","查询语录","语录查询"]

    查询目前只能查询语录总数
""".strip()
__plugin_des__ = "羽月语录给你力量"
__plugin_cmd__ = ["羽月语录"]
__plugin_version__ = 0.1
__plugin_type__ = ("语录", 1)
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["羽月语录", "羽月语录十连"],
}

quotations = on_command("羽月语录", aliases={"羽月语录"}, priority=5, block=True)
quotations_ten = on_command("羽月语录十连", aliases={"羽月语录十连"}, priority=5, block=True)

url = "http://sentence.osttsstudio.ltd:8000/?c=b"
CheckUrl = "http://sentence.osttsstudio.ltd:9000/b.json"

@quotations.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 1:
        data = (await AsyncHttpx.get(url, timeout=5)).json()
        result = f'{data["hitokoto"]}\t——{data["from_who"]} {data["id"]}'
        await quotations.send(result)
        logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + result
    )
    elif len(msg) == 1:
        SentenceCheck = msg[0]
        if SentenceCheck in ["查询","查询语录","语录查询"]:
            data = (await AsyncHttpx.get(CheckUrl, timeout=5)).json()
            result = str(len(data))
            await quotations.send(result)
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录查询:"
        + result
    )
        else:
            await quotations.finish("参数有误，请使用'帮助桑吉语录'查看帮助...")
    else:
        await quotations.finish("参数有误，请使用'帮助桑吉语录'查看帮助...")

@quotations_ten.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    for i in range(10):
        data = (await AsyncHttpx.get(url, timeout=5)).json()
        result = f'{data["hitokoto"]}\t | {data["from_who"]} {data["id"]}'
        await quotations_ten.send(result)
        logger.info(
            f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
            + result
        )

