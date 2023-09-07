from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
from configs.path_config import DATA_PATH, IMAGE_PATH
from models.level_user import LevelUser
from configs.config import Config
import os
import gc
import re
import json
import yaml
import random
import datetime

__zx_plugin_name__ = "楠桐语录"
__plugin_usage__ = """
usage：
    楠桐语录
    指令：
        "楠桐语录", "腩酮语录", "腩通语录", "腩桐语录", "喃酮语录", "喃铜语录", "喃通语录", "喃桐语录", "南酮语录", "南铜语录", "南桐语录", "南通语录"
        楠桐语录[“限定”, “指定”] 角色（必须为全名，可使用楠桐语录查询获取）
        楠桐语录n抽|单抽 例：楠桐语录30抽，楠桐语录14抽，楠桐语录单抽
        楠桐语录限定n抽 角色（必须为全名，可使用楠桐语录查询获取）
        楠桐语录 ["配置上限", "修改上限"] n | 可自定义n抽单次上限 该命令默认需要5级以上权限
        n抽触发正则：([0-9]+抽|零抽|单抽|抽|一井|抽卡)
        楠桐语录 ["查询","查询语录","语录查询"]
        楠桐语录 ["查询","查询语录","语录查询"] 显示/隐藏总数 | 显示/隐藏统计 | 显示/隐藏占比 | 显示/隐藏卡池
        楠桐语录 ["图片","图","截图"]

    累计抽卡数统计时间从2023.7.29 15:00开始

    错误码：
    10404：不存在的参数
    10001：参数不符合要求
    1012x：权限不足,x为所需权限
""".strip()
__plugin_des__ = "楠桐语录给你力量"
__plugin_cmd__ = ["楠桐语录"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["楠桐语录"],
}
__plugin_type__ = ("语录", 1)
__plugin_configs__ = {
    "SCU_DRAW_LEVEL": {
        "value": 5,
        "help": "群内修改抽卡上限需要的权限",
        "default_value": 5,
        "type": int,
    },
}
__plugin_cd_limit__ = {
    "cd": 10,                # 限制 cd 时长
    "check_type": "all",    # 'private'/'group'/'all'，限制私聊/群聊/全部
    "limit_type": "user",   # 监听对象，以user_id或group_id作为键来限制，'user'：用户id，'group'：群id
    "rst": "[uname]先生，bot已经被你塞满辣，等会儿再来噢铁汁",            # 回复的话，为None时不回复，可以添加[at]，[uname]，[nickname]来对应艾特，用户群名称，昵称系统昵称
    "status": True          # 此限制的开关状态
}

quotations = on_command("楠桐语录", aliases={"楠桐语录", "腩酮语录", "腩通语录", "腩桐语录", "喃酮语录", "喃铜语录", "喃通语录", "喃桐语录", "南酮语录", "南铜语录", "南桐语录", "南通语录"}, priority=5, block=True)

url = "http://sentence.osttsstudio.ltd:8000/?c=c"
CheckUrl = "http://sentence.osttsstudio.ltd:9000/c.json"

ScuDataPath = DATA_PATH / "scu"
ScuImagePath = IMAGE_PATH / "scu"
ScuImageGayPath = ScuImagePath / "gay"
CardCountPath = ScuDataPath / "card_count.json"
MainConfigPath = ScuDataPath / "config.yml"

if not os.path.exists(MainConfigPath):
    config = """
show:
  card_all: true
  list: true
  percent: true
  cardpool: true
"""
    with open(MainConfigPath, "w", encoding="utf-8") as f:
        yaml.dump(yaml.load(config, Loader=yaml.FullLoader), f)
count = {
    "n": 0,
    "r": 0,
    "sr": 0,
    "ssr": 0
}
if not ScuDataPath.exists():
    os.mkdir(ScuDataPath)
if not ScuImageGayPath.exists():
    os.mkdir(ScuImageGayPath)
if not CardCountPath.exists():
    with open(CardCountPath, "w", encoding="utf-8") as cc:
        json.dump(count, cc, ensure_ascii=False)

@quotations.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    f = open("/root/sentences/sentences/c.json", 'r', encoding="utf-8") # 将文件写入缓存
    n = []
    r = []
    sr = []
    ssr = []
    text = f.read()
    f.close() # 关闭文件
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
        if not "晨于曦Asahi" in n:
            n.append("晨于曦Asahi")
            if "晨于曦Asahi" in r:
                r.remove("晨于曦Asahi")
            elif "晨于曦Asahi" in sr:
                sr.remove("晨于曦Asahi")
            elif "晨于曦Asahi" in ssr:
                ssr.remove("晨于曦Asahi")
        if key in n:
            n_all += int(value)
        elif key in r:
            r_all += int(value)
        elif key in sr:
            sr_all += int(value)
        elif key in ssr:
            ssr_all += int(value)
    CardPool = n + r + sr + ssr

    CountJson = open(CardCountPath,'r')
    c = CountJson.read()
    CountJson.close()
    CountList = json.loads(c)
    DrawYaml = open(MainConfigPath, 'r')
    dj = DrawYaml.read()
    DrawYaml.close()
    MaxDrawCountLoad = yaml.load(dj, Loader=yaml.FullLoader)

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
        with open(CardCountPath,'w',encoding='utf-8') as f:
            json.dump(CountList, f,ensure_ascii=False)
        result = f'〔g{data["id"]}〕 {data["hitokoto"]} | {data["from_who"]}{card}'
        await quotations.send(result)
        logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + result
    )
        flush = gc.collect()
        print(f"已成功清理内存：{flush}")
    elif len(msg) >= 1:
        SentenceCheck = msg[0]
        DrawRegex = re.match(r"([0-9]+抽|零抽|单抽|抽|一井|抽卡)", SentenceCheck)
        if SentenceCheck in ["配置上限", "修改上限"]:
            if isinstance(event, GroupMessageEvent):
                if not await LevelUser.check_level(
                    event.user_id,
                    event.group_id,
                    Config.get_config("gay_quotations", "SCU_DRAW_LEVEL"),
                ):
                    await quotations.finish(
                        f"发生错误！code:1012{Config.get_config('gay_quotations', 'SCU_DRAW_LEVEL')}",
                        at_sender=False
                    )
            MaxDrawCountLoad[f"{event.group_id}"] = int(msg[1])
            with open(MainConfigPath,'w',encoding='utf-8') as f:
                yaml.dump(MaxDrawCountLoad, f)

            MaxCountError = 30
            if int(msg[1]) > int(MaxCountError):
                result = f"已成功配置抽卡上限为{msg[1]}，警告！超过 {MaxCountError} 将会使bot发送过长的消息，存在被风控的风险！"
            else:
                result = f"已成功配置抽卡上限为{msg[1]}"
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 配置楠桐语录抽卡上限:{msg[1]}"
    )
            await quotations.send(result)
        elif SentenceCheck in ["限定", "指定"]:
            DrawAuthor = msg[1]
            Draw = 1
            DrawAuthorCount = 0
            while Draw == 1:
                data = (await AsyncHttpx.get(url, timeout=10)).json()
                DrawAuthorCount += 1
                if data["from_who"] == DrawAuthor:
                    break
                elif DrawAuthorCount == 1000:
                    break
            if DrawAuthorCount == 1000:
                result = f"抽了{DrawAuthorCount}次都没抽到，你真是个非酋"
            else:
                result = f'〔g{data["id"]}〕 {data["hitokoto"]} | {data["from_who"]} | 抽取次数：{DrawAuthorCount}'
            await quotations.send(result)
            logger.info(
            f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
            + result
        )
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")
        elif re.match(r"(限定|指定)([0-9]+抽|零抽|单抽|抽|一井|抽卡)", SentenceCheck):
            try:
                MaxCount = MaxDrawCountLoad[f"{event.group_id}"]
            except:
                MaxDrawCountLoad[f"{event.group_id}"] = 50
                with open(MainConfigPath,'w',encoding='utf-8') as f:
                    yaml.dump(MaxDrawCountLoad, f)
                await quotations.finish("未配置抽卡上限，已默认配置为50发，请重新抽取！")
            DrawCount = SentenceCheck
            if not SentenceCheck in ["限定抽", "限定抽卡", "限定单抽"]:
                DrawCount = str(SentenceCheck).replace("限定", "").replace("抽", "")
            if SentenceCheck in ["限定一井", "指定一井"]:
                DrawCount = MaxCount
            if SentenceCheck in ["限定单抽", "指定单抽"]:
                DrawCount = 1
            if DrawCount == "" or SentenceCheck in ["限定0抽", "限定零抽", "限定抽卡", "指定0抽", "指定零抽", "指定抽卡"]:
                await quotations.finish("虚空抽卡？")
            elif int(DrawCount) > int(MaxCount):
                await quotations.finish(f"孩子塞不下辣，最多只能塞{MaxCount}发!")

            data = []
            MaxDrawCount = 500
            for i in range(int(DrawCount)):
                Draw = 1
                DrawAuthorCount = 0
                DrawAuthor = msg[1]
                while Draw == 1:
                    text = (await AsyncHttpx.get(url, timeout=10)).json()
                    DrawAuthorCount += 1
                    if text["from_who"] == DrawAuthor:
                        break
                    elif DrawAuthorCount == int(MaxDrawCount):
                        break
                result = f'〔g{text["id"]}〕 {text["hitokoto"]} | {text["from_who"]} | 抽取次数：{DrawAuthorCount}'
                data.append(result)

            if DrawAuthorCount == int(MaxDrawCount):
                result = f"抽了{MaxDrawCount * DrawCount}次都没抽到，你真是个非酋"
            else:
                result = str(data).replace("[", "").replace("]", "").replace(", ", "\n").replace("'", "")
            
            await quotations.send(result)
            logger.info(
                f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
                + str(result)
            )
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")

        elif SentenceCheck in ["查询","查询语录","语录查询"]:
            with open(MainConfigPath, "r", encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            if len(msg) >= 2:
                CmdMsg = msg[1]
                if CmdMsg in ["显示总数", "隐藏总数", "显示统计", "隐藏统计", "显示占比", "隐藏占比", "显示卡池", "隐藏卡池"]:
                    if CmdMsg == "显示总数":
                        config["show"]["card_all"] = True
                    elif CmdMsg == "隐藏总数":
                        config["show"]["card_all"] = False
                    elif CmdMsg == "显示统计":
                        config["show"]["list"] = True
                    elif CmdMsg == "隐藏统计":
                        config["show"]["list"] = False
                    elif CmdMsg == "显示占比":
                        config["show"]["percent"] = True
                    elif CmdMsg == "隐藏占比":
                        config["show"]["percent"] = False
                    elif CmdMsg == "显示卡池":
                        config["show"]["cardpool"] = True
                    elif CmdMsg == "隐藏卡池":
                        config["show"]["cardpool"] = False
                    with open(MainConfigPath, "w") as f:
                        yaml.dump(config, f)
                    await quotations.finish(f"已成功{CmdMsg}!")
            List = "\n" + str(Dict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
            percent = "\n" + str(NewDict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
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
            CountJson = open(CardCountPath, 'r')
            c = CountJson.read()
            CountJson.close()
            CountList = json.loads(c)
            CardDict = {}
            DrawCountCheck = CountList["n"] + CountList["r"] + CountList["sr"] + CountList["ssr"]
            for CardKey,CardValue in CountList.items():
                CardValue = f"{int(CardValue / DrawCountCheck * 10000) / 100}"
                CardDict[CardKey] = f"{CardValue}%"
            DrawPercent = str(CardDict).replace("'", "").replace(", ", " | ").replace("{", "").replace("}", "")
            CardCount = str(CountList).replace("{", "").replace("}", "").replace("'", "").replace(",", "")
            card_all = str(len(content))
            ShowCardPool = f"""
N：{n} | {n_all}条
R：{r} | {r_all}条
SR：{sr} | {sr_all}条
SSR：{ssr} | {ssr_all}条
"""
            with open(MainConfigPath, "r", encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            if not config["show"]["card_all"]:
                card_all = "**"
            if not config["show"]["list"]:
                List = "**"
            if not config["show"]["percent"]:
                percent = "**"
            if not config["show"]["cardpool"]:
                ShowCardPool = "**\n"
            result = f"""语录总数：{card_all}

统计：{List}

占比：{percent}

卡池：{ShowCardPool}
累计总数：{DrawCountCheck}
累计抽卡：{CardCount} 
累计概率：{DrawPercent}
统计区间：2023.07.29 15:00 - {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}"""
            await quotations.send(result)
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录查询:"
        + result
    )
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")

        elif SentenceCheck in ["图片","图","截图"]:
            length = len(os.listdir(ScuImageGayPath))
            if length == 0:
                logger.warning(f"图库 '楠桐' 为空，调用取消！")
                await quotations.finish("该图库中没有图片噢")
            index = os.listdir(ScuImageGayPath)
            img = random.choice(index)
            result = image("scu/gay/" + str(img))
            if result:
                logger.info(
                    f"发送:" + result,
                    "发送图片",
                    event.user_id,
                    getattr(event, "group_id", None),
                )
                await quotations.send(result)
                flush = gc.collect()
                print(f"已成功清理内存：{flush}")
            else:
                logger.info(
                    f"发送失败",
                    "发送图片",
                    event.user_id,
                    getattr(event, "group_id", None),
                )
                await quotations.finish(f"发生错误！")
                flush = gc.collect()
                print(f"已成功清理内存：{flush}")

        elif DrawRegex:
            try:
                MaxCount = MaxDrawCountLoad[f"{event.group_id}"]
            except:
                MaxDrawCountLoad[f"{event.group_id}"] = 50
                with open(MainConfigPath,'w',encoding='utf-8') as f:
                    yaml.dump(MaxDrawCountLoad, f)
                await quotations.finish("未配置抽卡上限，已默认配置为50发，请重新抽取！")
            DrawCount = SentenceCheck
            if not SentenceCheck in ["抽", "抽卡", "单抽"]:
                DrawCount = str(SentenceCheck).replace("抽", "")
            if SentenceCheck == "一井":
                DrawCount = MaxCount
            if SentenceCheck == "单抽":
                DrawCount = 1
            if DrawCount == "" or SentenceCheck in ["0抽", "零抽", "抽卡"]:
                await quotations.finish("虚空抽卡？")
            elif int(DrawCount) > int(MaxCount):
                await quotations.finish(f"孩子塞不下辣，最多只能塞{MaxCount}发!")

            data = []
            card_n, card_r, card_sr, card_ssr = 0, 0, 0, 0

            for i in range(int(DrawCount)):
                text = (await AsyncHttpx.get(url, timeout=10)).json()
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
                hitokoto = f'〔g{text["id"]}〕 {text["hitokoto"]} | {text["from_who"]}{card}'
                data.append(hitokoto)

            with open(CardCountPath,'w',encoding='utf-8') as f:
                json.dump(CountList, f,ensure_ascii=False)
            result = str(data).replace("[", "").replace("]", "").replace(", ", "\n").replace("'", "") + f"\n\n汇总：N：{card_n} R：{card_r} SR：{card_sr} SSR：{card_ssr}"
            await quotations.send(result)
            logger.info(
                f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
                + str(result)
            )
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")
        else:
            await quotations.finish("参数有误,code:10404，请使用'帮助楠桐语录'查看帮助...")
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")
    else:
        await quotations.finish("参数有误,code:20001，请使用'帮助楠桐语录'查看帮助...")
        flush = gc.collect()
        print(f"已成功清理内存：{flush}")