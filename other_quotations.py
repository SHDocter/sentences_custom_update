from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
import os
import json
import random

__zx_plugin_name__ = "语录合集"
__plugin_usage__ = """
usage：
    语录
    指令：
        语录合集
        语录合集十连
        语录合集 随机
        语录合集 ["查询","查询语录","语录查询"]
        语录合集 ["图片","图","截图"]

    查询目前只能查询语录总数
    随机抽取范围为整个语录
""".strip()
__plugin_des__ = "语录合集给你力量"
__plugin_cmd__ = ["语录合集"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["语录", "语录十连"],
}
__plugin_type__ = ("语录", 1)

quotations = on_command("语录合集", aliases={"语录合集"}, priority=5, block=True)
quotations_ten = on_command("语录合集十连", aliases={"语录合集十连"}, priority=5, block=True)

url = "http://sentence.osttsstudio.ltd:8000/?c=e"
CheckUrl = "http://sentence.osttsstudio.ltd:9000/e.json"

@quotations.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 1:
        data = (await AsyncHttpx.get(url, timeout=5)).json()
        result = f'{data["hitokoto"]}\t | {data["from_who"]} {data["id"]}'
        await quotations.send(result)
        logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + result
    )
    elif len(msg) == 1:
        SentenceCheck = msg[0]
        if SentenceCheck in ["查询","查询语录","语录查询"]:
            f = open("/root/sentences/sentences/e.json", 'r', encoding="utf-8") # 将语言文件写入缓存
            n = []
            r = []
            sr = []
            ssr = []
            text = f.read() # 读取语言
            f.close() # 关闭语言文件
            content = json.loads(text) # 转为List，List中为字典

            List = []
            for _ in content:
                AuthorList = _["from_who"]
                List.append(AuthorList)
            dict = {}
            for key in List:
                dict[key] = dict.get(key, 0) + 1
            NewDict = {}
            for key,value in dict.items():
                value = f"{int(value / len(content) * 10000) / 100}"
                NewDict[key] = f"{value}%"
                if float(value) <= 2.0:
                    ssr.append(key)
                elif float(value) <= 10.0:
                    sr.append(key)
                elif float(value) <= 25.0:
                    r.append(key)
                else:
                    n.append(key)
            list = str(dict).replace("'", "").replace(", ", "\n").replace("{", "").replace("}", "")
            percent = str(NewDict).replace("'", "").replace(", ", "\n").replace("{", "").replace("}", "")
            n = str(n).replace(", ", " ").replace("[", "").replace("]", "").replace("'", "")
            r = str(r).replace(", ", " ").replace("[", "").replace("]", "").replace("'", "")
            sr = str(sr).replace(", ", " ").replace("[", "").replace("]", "").replace("'", "")
            ssr = str(ssr).replace(", ", " ").replace("[", "").replace("]", "").replace("'", "")
            if n == "":
                n = "无"
            if r == "":
                r = "无"
            if sr == "":
                sr = "无"
            if ssr == "":
                ssr = "无"
            result = f"语录总数：{str(len(content))}\n\n统计：\n{list}\n\n占比：\n{percent}\n\n卡池：\nN：{n}\nR：{r}\nSR：{sr}\nSSR：{ssr}"
            await quotations.send(result)
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录查询:"
        + result
    )
        elif SentenceCheck in ["图片","图","截图"]:
            ScuPath = "/home/zhenxun_bot-main/resources/image/scu/other/"
            length = len(os.listdir(ScuPath))
            if length == 0:
                logger.warning(f"图库 '合集' 为空，调用取消！")
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
        elif SentenceCheck in ["随机"]:
            data = (await AsyncHttpx.get("http://sentence.osttsstudio.ltd:8000", timeout=5)).json()
            result = f'{data["hitokoto"]} | {data["from_who"]} {data["type"]}:{data["id"]}'
            await quotations.send(result)
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录查询:"
        + result
    )
        else:
            await quotations.finish("参数有误，请使用'帮助语录'查看帮助...")
    else:
        await quotations.finish("参数有误，请使用'帮助语录'查看帮助...")

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