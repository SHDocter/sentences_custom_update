from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
import os
import re
import json
import random
import datetime

__zx_plugin_name__ = "楠桐语录"
__plugin_usage__ = """
usage：
    楠桐语录
    指令：
        楠桐语录
        楠桐语录十连
        楠桐语录 ["查询","查询语录","语录查询"]
        楠桐语录 ["图片","图","截图"]

累计抽卡数统计时间从2023.7.29 15:00开始
""".strip()
__plugin_des__ = "楠桐语录给你力量"
__plugin_cmd__ = ["楠桐语录"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["楠桐语录", "楠桐语录十连"],
}
__plugin_type__ = ("语录", 1)

quotations = on_command("楠桐语录", aliases={"楠桐语录"}, priority=5, block=True)
quotations_ten = on_command("楠桐语录十连", aliases={"楠桐语录十连"}, priority=5, block=True)

url = "http://sentence.osttsstudio.ltd:8000/?c=c"
CheckUrl = "http://sentence.osttsstudio.ltd:9000/c.json"

@quotations.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    f = open("/root/sentences/sentences/c.json", 'r', encoding="utf-8") # 将语言文件写入缓存
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
    Dict = {}
    for key in List:
        Dict[key] = Dict.get(key, 0) + 1
    NewDict = {}
    n_all = 0
    r_all = 0
    sr_all = 0
    ssr_all = 0
    for key,value in Dict.items():
        ValuePercent = f"{int(value / len(content) * 10000) / 100}"
        NewDict[key] = f"{ValuePercent}%"
        if float(ValuePercent) <= 2.0:
            ssr.append(key)
        elif float(ValuePercent) <= 10.0:
            sr.append(key)
        elif float(ValuePercent) <= 25.0:
            r.append(key)
        else:
            n.append(key)
        if key in n:
            n_all += int(value)
        elif key in r:
            r_all += int(value)
        elif key in sr:
            sr_all += int(value)
        elif key in ssr:
            ssr_all += int(value)
    CardPool = n + r + sr + ssr

    CountJson = open("/home/zhenxun_bot-main/resources/json/scu/card_count.json",'r')
    c = CountJson.read()
    CountJson.close()
    CountList = json.loads(c)

    if len(msg) < 1:
        data = (await AsyncHttpx.get(url, timeout=5)).json()
        card = ""
        if data["from_who"] in n:
            card = " | N卡"
            CountList["n"] += 1
        if data["from_who"] in r:
            card = " | R卡"
            CountList["r"] += 1
        if data["from_who"] in sr:
            card = " | SR卡"
            CountList["sr"] += 1
        if data["from_who"] in ssr:
            card = " | SSR卡"
            CountList["ssr"] += 1
        if data["from_who"] not in CardPool:
            card = ""
        with open("/home/zhenxun_bot-main/resources/json/scu/card_count.json",'w',encoding='utf-8') as f:
            json.dump(CountList, f,ensure_ascii=False)
        result = f'〔c{data["id"]}〕 {data["hitokoto"]} | {data["from_who"]}{card}'
        await quotations.send(result)
        logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + result
    )
    elif len(msg) == 1:
        SentenceCheck = msg[0]
        if SentenceCheck in ["查询","查询语录","语录查询"]:
            list = str(Dict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
            percent = str(NewDict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
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
            CountJson = open("/home/zhenxun_bot-main/resources/json/scu/card_count.json",'r')
            c = CountJson.read()
            CountJson.close()
            CountList = json.loads(c)
            CardDict = {}
            DrawCount = CountList["n"] + CountList["r"] + CountList["sr"] + CountList["ssr"]
            for CardKey,CardValue in CountList.items():
                CardValue = f"{int(CardValue / DrawCount * 10000) / 100}"
                CardDict[CardKey] = f"{CardValue}%"
            DrawPercent = str(CardDict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
            CardCount = str(CountList).replace("{", "").replace("}", "").replace("'", "").replace(",", "")
            result = f"""语录总数：{str(len(content))}

统计：
{list}

占比：
{percent}

卡池：
N：{n} | {n_all}条
R：{r} | {r_all}条
SR：{sr} | {sr_all}条
SSR：{ssr} | {ssr_all}条

累计总数：{DrawCount}
累计抽卡：{CardCount} 
累计概率：{DrawPercent}
统计区间：2023.07.29 15:00 - {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}"""
            await quotations.send(result)
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录查询:"
        + result
    )
        elif SentenceCheck in ["图片","图","截图"]:
            ScuPath = "/home/zhenxun_bot-main/resources/image/scu/gay/"
            length = len(os.listdir(ScuPath))
            if length == 0:
                logger.warning(f"图库 '楠桐' 为空，调用取消！")
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
            await quotations.finish("参数有误，请使用'帮助楠桐语录'查看帮助...")
    else:
        await quotations.finish("参数有误，请使用'帮助楠桐语录'查看帮助...")

@quotations_ten.handle()
async def _(event: MessageEvent):
    f = open("/root/sentences/sentences/c.json", 'r', encoding="utf-8") # 将语言文件写入缓存
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
    Dict = {}
    for key in List:
        Dict[key] = Dict.get(key, 0) + 1
    NewDict = {}
    for key,value in Dict.items():
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
    CardPool = n + r + sr + ssr
    data = []
    card_n, card_r, card_sr, card_ssr = 0, 0, 0, 0

    CountJson = open("/home/zhenxun_bot-main/resources/json/scu/card_count.json",'r')
    c = CountJson.read()
    CountJson.close()
    CountList = json.loads(c)

    for i in range(10):
        text = (await AsyncHttpx.get(url, timeout=5)).json()
        card = ""
        if text["from_who"] in n:
            card = " | N卡"
            card_n += 1
            CountList["n"] += 1
        else:
            card_n
        if text["from_who"] in r:
            card = " | R卡"
            card_r += 1
            CountList["r"] += 1
        else:
            card_r
        if text["from_who"] in sr:
            card = " | SR卡"
            card_sr += 1
            CountList["sr"] += 1
        else:
            card_sr
        if text["from_who"] in ssr:
            card = " | SSR卡"
            card_ssr += 1
            CountList["ssr"] += 1
        else:
            card_ssr
        if text["from_who"] not in CardPool:
            card = ""
        hitokoto = f'〔c{text["id"]}〕 {text["hitokoto"]} | {text["from_who"]}{card}'
        data.append(hitokoto)

    with open("/home/zhenxun_bot-main/resources/json/scu/card_count.json",'w',encoding='utf-8') as f:
        json.dump(CountList, f,ensure_ascii=False)
    result = str(data).replace("[", "").replace("]", "").replace(", ", "\n").replace("'", "") + f"\n\n汇总：N：{card_n} R：{card_r} SR：{card_sr} SSR：{card_ssr}"
    await quotations_ten.send(result)
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + str(result)
    )