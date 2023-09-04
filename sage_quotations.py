from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
import os
import random

__zx_plugin_name__ = "桑吉语录"
__plugin_usage__ = """
usage：
    桑吉语录
    指令：
        桑吉语录
        桑吉语录十连
        桑吉语录 ["查询","查询语录","语录查询"]
        桑吉语录 ["图片","图","截图"]

    查询目前只能查询语录总数
""".strip()
__plugin_des__ = "桑吉语录给你力量"
__plugin_cmd__ = ["桑吉语录"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["桑吉语录", "桑吉语录十连"],
}
__plugin_type__ = ("语录", 1)

quotations = on_command("桑吉语录", aliases={"桑吉语录", "桑急语录", "羊驼语录"}, priority=5, block=True)
quotations_ten = on_command("桑吉语录十连", aliases={"桑吉语录十连", "桑急语录十连", "羊驼语录十连"}, priority=5, block=True)

url = "http://sentence.osttsstudio.ltd:8000/?c=a"
CheckUrl = "http://sentence.osttsstudio.ltd:9000/a.json"

@quotations.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 1:
        data = (await AsyncHttpx.get(url, timeout=5)).json()
        result = f'{data["hitokoto"]} | {data["from_who"]} {data["id"]}'
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
        elif SentenceCheck in ["图片","图","截图"]:
            ScuPath = "/home/zhenxun_bot-main/resources/image/scu/sage/"
            length = len(os.listdir(ScuPath))
            if length == 0:
                logger.warning(f"图库 '桑吉' 为空，调用取消！")
                await quotations.finish("该图库中没有图片噢")
            index = os.listdir(ScuPath)
            img = random.choice(index)
            result = image(ScuPath + str(img))
            if result:
                logger.info(
                    f"发送:" + result,
                    "发送图片",
                    event.user_id,
                    getattr(event, "group_id", None),
                )
                await quotations.send(result)
            else:
                logger.info(
                    f"发送失败",
                    "发送图片",
                    event.user_id,
                    getattr(event, "group_id", None),
                )
                await quotations.finish(f"发生错误！")
        else:
            await quotations.finish("参数有误，请使用'帮助桑吉语录'查看帮助...")
    else:
        await quotations.finish("参数有误，请使用'帮助桑吉语录'查看帮助...")

@quotations_ten.handle()
async def _(event: MessageEvent):
    data = []
    for i in range(10):
        text = (await AsyncHttpx.get(url, timeout=5)).json()
        hitokoto = f'{text["hitokoto"]} | {text["from_who"]} {text["id"]}\n'
        data.append(hitokoto)
    result = data
    await quotations_ten.send(result)
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + str(result)
    )