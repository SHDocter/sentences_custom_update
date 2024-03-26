'''
Author: Nya-WSL
Copyright © 2023 by Nya-WSL All Rights Reserved. 
Date: 2023-11-01 12:24:49
LastEditors: 狐日泽
'''
from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
from configs.path_config import DATA_PATH, IMAGE_PATH
from models.level_user import LevelUser
from configs.config import Config
from . import db
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
        楠桐语录 稀有度 查询
        楠桐语录稀有度 ssr/SSR 百分比(浮点数) | 楠桐语录 稀有度 角色 ssr/SSR
        例：楠桐语录稀有度 ssr 2.0 | 楠桐语录稀有度 晨于曦Asahi ssr
        楠桐语录 统计
        楠桐语录 统计 关键词(支持字典)

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
    "SCU_CHANGE_CARD_PERCENT": {
        "value": 6,
        "help": "群内调整卡池百分比需要的权限",
        "default_value": 6,
        "type": int,
    },
    "SCU_CHANGE_CARD_USER": {
        "value": 6,
        "help": "群内调整角色卡池需要的权限",
        "default_value": 6,
        "type": int,
    }
}
__plugin_cd_limit__ = {
    "cd": 10,                # 限制 cd 时长
    "check_type": "all",    # 'private'/'group'/'all'，限制私聊/群聊/全部
    "limit_type": "user",   # 监听对象，以user_id或group_id作为键来限制，'user'：用户id，'group'：群id
    "rst": "[uname]先生，bot已经被你塞满辣，等会儿再来噢铁汁",            # 回复的话，为None时不回复，可以添加[at]，[uname]，[nickname]来对应艾特，用户群名称，昵称系统昵称
    "status": True          # 此限制的开关状态
}

quotations = on_command("楠桐语录", aliases={"楠桐语录", "腩酮语录", "腩通语录", "腩桐语录", "喃酮语录", "喃铜语录", "喃通语录", "喃桐语录", "南酮语录", "南铜语录", "南桐语录", "南通语录"}, priority=5, block=True)

url = "http://sentence.nya-wsl.cn:8000/?c=c"
EndTime = datetime.datetime(2023, 12, 26)

ScuDataPath = DATA_PATH / "scu"
ScuImagePath = IMAGE_PATH / "scu"
ScuImageGayPath = ScuImagePath / "gay"
MainConfigPath = ScuDataPath / "config.yml"
CardCountPath = ScuDataPath / "card_count.json"
CardDictPath = ScuDataPath / "card_dict.json"
UserDictPath = ScuDataPath / "user_dict.json"
DatabasePath = ScuDataPath / "gay_quotations.db"

if not os.path.exists(DatabasePath):
    db.create()

if not os.path.exists(UserDictPath):
    with open(UserDictPath, "w", encoding="utf-8") as ud:
        ud.write(r"{}")

if not os.path.exists(MainConfigPath):
    config = """
percent:
  r: '25.0'
  sr: '10.0'
  ssr: '2.0'
show:
  card_all: true
  list: true
  percent: true
  cardpool: true
"""
    with open(MainConfigPath, "w", encoding="utf-8") as f:
        yaml.dump(yaml.load(config, Loader=yaml.FullLoader), f)
if not os.path.exists(CardDictPath):
    with open(CardDictPath, "w", encoding="utf-8") as f:
        f.write(r"{}")
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
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    with open(UserDictPath, "r", encoding="utf-8") as ud:
        UserDict = json.load(ud)
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
    NameRegexList = []
    for _ in content:
        AuthorList = _["from_who"]
        NameList = _["hitokoto"]
        NameRegexList.append(NameList)
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
        #ValuePercent = f"{int(value / len(content) * 10000) / 100}"
        #NewDict[key] = f"{ValuePercent}%"
        ValuePercent = float(int(value / len(content) * 10000) / 100)
        NewDict[key] = ValuePercent
        if len(msg) >= 2:
            with open(MainConfigPath, "r", encoding="utf-8") as mcp:
                conf = yaml.load(mcp, Loader=yaml.FullLoader)
            with open(CardDictPath, "r", encoding="utf-8") as cdp:
                CustomCard = json.load(cdp)
            if msg[0] == "稀有度":
                if msg[1] == "调整":
                    if len(msg) < 4:
                        await quotations.finish("发生错误！code:10001")
                    if isinstance(event, GroupMessageEvent):
                        if not await LevelUser.check_level(
                            event.user_id,
                            event.group_id,
                            Config.get_config("gay_quotations", "SCU_CHANGE_CARD_USER"),
                        ):
                            await quotations.finish(
                                f"发生错误！code:1012{Config.get_config('gay_quotations', 'SCU_CHANGE_CARD_USER')}",
                                at_sender=False
                            )
                    author = str(msg[2])
                    for key,value in UserDict.items():
                        if key == author:
                            author = value
                    CustomCard[author] = msg[3]
                elif msg[1] == "查询":
                    result = f'ssr：{conf["percent"]["ssr"]}% | sr：{conf["percent"]["sr"]}% | r：{conf["percent"]["r"]}%'
                    await quotations.finish(result)
                if isinstance(event, GroupMessageEvent):
                    if not await LevelUser.check_level(
                        event.user_id,
                        event.group_id,
                        Config.get_config("gay_quotations", "SCU_CHANGE_CARD_PERCENT"),
                    ):
                        await quotations.finish(
                            f"发生错误！code:1012{Config.get_config('gay_quotations', 'SCU_CHANGE_CARD_PERCENT')}",
                            at_sender=False
                        )
                if msg[1] in ["ssr", "SSR"]:
                    conf["percent"]["ssr"] = msg[2]
                if msg[1] in ["sr", "SR"]:
                    conf["percent"]["sr"] = msg[2]
                if msg[1] in ["r", "R"]:
                    conf["percent"]["r"] = msg[2]
                with open(MainConfigPath, "w", encoding="utf-8") as mcp:
                    yaml.dump(conf, mcp)
                with open(CardDictPath, "w", encoding="utf-8") as cdp:
                    json.dump(CustomCard, cdp, ensure_ascii=False)
                await quotations.finish("已成功调整稀有度！")

        with open(MainConfigPath, "r", encoding="utf-8") as mcp:
            conf = yaml.load(mcp, Loader=yaml.FullLoader)
        with open(CardDictPath, "r", encoding="utf-8") as cdp:
            CustomCard = json.load(cdp)
        percent_ssr = conf["percent"]["ssr"]
        percent_sr = conf["percent"]["sr"]
        percent_r = conf["percent"]["r"]
        if float(ValuePercent) <= float(percent_ssr):
            ssr.append(key)
        elif float(ValuePercent) <= float(percent_sr):
            sr.append(key)
        elif float(ValuePercent) <= float(percent_r):
            r.append(key)
        else:
            n.append(key)
        for author,card_valve in CustomCard.items():
            if card_valve in ["n", "N"]:
                if author in n:
                    n.remove(author)
                if not author in n:
                    n.append(author)
                if author in r:
                    r.remove(author)
                elif author in sr:
                    sr.remove(author)
                elif author in ssr:
                    ssr.remove(author)
            elif card_valve in ["r", "R"]:
                if author in r:
                    r.remove(author)
                if not author in r:
                    r.append(author)
                if author in n:
                    n.remove(author)
                elif author in sr:
                    sr.remove(author)
                elif author in ssr:
                    ssr.remove(author)
            elif card_valve in ["sr", "SR"]:
                if author in sr:
                    sr.remove(author)
                if not author in sr:
                    sr.append(author)
                if author in r:
                    r.remove(author)
                elif author in n:
                    n.remove(author)
                elif author in ssr:
                    ssr.remove(author)
            elif card_valve in ["ssr", "SSR"]:
                if author in ssr:
                    ssr.remove(author)
                if not author in ssr:
                    ssr.append(author)
                if author in r:
                    r.remove(author)
                elif author in sr:
                    sr.remove(author)
                elif author in n:
                    n.remove(author)
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
        DatabaseDict = {"N": 0,"R": 0, "SR": 0, "SSR": 0}
        up_user = "晨于曦Asahi"
        up_percent = 40
        if data["from_who"] != up_user:
            print(f"未抽中{up_user}，判定概率：{up_percent}%，正在判定...")
            if random.randint(1, 100) <= int(up_percent):
                await quotations.send(f"判定成功，将随机抽取一张{up_user}替换卡面...")
                data = (await AsyncHttpx.get(url, timeout=5)).json()
                while data["from_who"] != up_user:
                    print(f"未抽中{up_user}，继续抽取...")
                    data = (await AsyncHttpx.get(url, timeout=5)).json()
                else:
                    print("抽取成功，内容：" + str({data["hitokoto"]}))
            else:
                print(f"判定失败！将跳过抽取{up_user}...")
        if data["from_who"] in n:
            card = " | N卡"
            CountList["n"] += 1
            DatabaseDict["N"] = DatabaseDict["N"] + 1
        if data["from_who"] in r:
            card = " | R卡"
            CountList["r"] += 1
            DatabaseDict["R"] = DatabaseDict["R"] + 1
        if data["from_who"] in sr:
            card = " | SR卡"
            CountList["sr"] += 1
            DatabaseDict["SR"] = DatabaseDict["SR"] + 1
        if data["from_who"] in ssr:
            card = " | SSR卡"
            CountList["ssr"] += 1
            DatabaseDict["SSR"] = DatabaseDict["SSR"] + 1
        if data["from_who"] not in CardPool:
            card = ""
        with open(CardCountPath,'w',encoding='utf-8') as f:
            json.dump(CountList, f,ensure_ascii=False)
        if db.check(str(event.user_id)) != []:
            db.uptate(event.user_id, CountDict=DatabaseDict)
        else:
            db.write(event.user_id, event.group_id)
            db.uptate(event.user_id, CountDict=DatabaseDict)
        if datetime.datetime.now() < EndTime:
            if data["from_who"] in ['稻荷神的灵狐', '高橋はるき', '浅律', '晨于曦Asahi', '桑吉Sage']:
                card = " | UR卡"
        result = f'〔g{data["id"]}〕 {data["hitokoto"]} | {data["from_who"]}{card}'
        await quotations.send(result)
        logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 发送语录:"
        + result
    )
        flush = gc.collect()
        print(f"已清理内存：{flush}")
    elif len(msg) >= 1:
        SentenceCheck = msg[0]
        DrawRegex = re.match(r"([0-9]+抽|零抽|单抽|抽|一井|抽卡)", SentenceCheck)
        # UpPoolRegex = re.match(r"(up|UP)池", SentenceCheck)
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
            result = f"已成功配置抽卡上限为{msg[1]}发"
            logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 配置楠桐语录抽卡上限:{msg[1]}"
    )
            await quotations.send(result)
        elif SentenceCheck in ["限定", "指定"]:
            DrawAuthor = msg[1]
            for key,value in UserDict.items():
                if key == DrawAuthor:
                    DrawAuthor = value
            DrawAuthorCount = 0
            msg_list = []
            while True:
                data = (await AsyncHttpx.get(url, timeout=10)).json()
                DrawAuthorCount += 1
                if data["from_who"] == DrawAuthor:
                    break
                elif DrawAuthorCount == 500:
                    break
            if DrawAuthorCount == 500:
                result = f"抽了{DrawAuthorCount}次都没抽到，你真是个非酋"
                await quotations.send(result)
            else:
                result = f'〔g{data["id"]}〕 {data["hitokoto"]} | {data["from_who"]} | 抽取次数：{DrawAuthorCount}'
            await quotations.send(result)
            flush = gc.collect()
            print(f"已清理内存：{flush}")
        elif re.match(r"(限定|指定)([0-9]+抽|零抽|单抽|抽|一井|抽卡)", SentenceCheck):
            try:
                MaxCount = MaxDrawCountLoad[f"{event.group_id}"]
            except:
                MaxDrawCountLoad[f"{event.group_id}"] = 50
                MaxCount = 50
                with open(MainConfigPath,'w',encoding='utf-8') as f:
                    yaml.dump(MaxDrawCountLoad, f)
                await quotations.send("未配置抽卡上限，已默认配置为50发！")
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

            msg_list = []
            MaxDrawCount = 500
            for i in range(int(DrawCount)):
                DrawAuthorCount = 0
                DrawAuthor = msg[1]
                for key,value in UserDict.items():
                    if key == DrawAuthor:
                        DrawAuthor = value
                while True:
                    text = (await AsyncHttpx.get(url, timeout=10)).json()
                    DrawAuthorCount += 1
                    if text["from_who"] == DrawAuthor:
                        break
                    elif DrawAuthorCount == int(MaxDrawCount):
                        break
                data = {
            "type": "node",
            "data": {"name": "楠桐语录", "uin": f"{bot.self_id}", "content": f'〔g{text["id"]}〕 {text["hitokoto"]} | {text["from_who"]} | 抽取次数：{DrawAuthorCount}'},
        }
                msg_list.append(data)

            if DrawAuthorCount == int(MaxDrawCount):
                result = f"抽了{MaxDrawCount * DrawCount}次都没抽到，你真是个非酋"
                await quotations.send(result)
            else:
                await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
            
            flush = gc.collect()
            print(f"已清理内存：{flush}")

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
            Dict = sorted(Dict.items(), key=lambda x:x[1], reverse=True)
            NewDict = sorted(NewDict.items(), key=lambda x:x[1], reverse=True)
            List = "\n" + str(Dict).replace("[('", "").replace("), ('", " | ").replace("', ", "：").replace(")]", "")
            percent = "\n" + str(NewDict).replace("[('", "").replace("), ('", "% | ").replace("', ", "：").replace(")]", "%")
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
            data = {
            "type": "node",
            "data": {"name": "楠桐语录", "uin": f"{bot.self_id}", "content": result},
        }
            await bot.send_group_forward_msg(group_id=event.group_id, messages=data)
            flush = gc.collect()
            print(f"已清理内存：{flush}")

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
                print(f"已清理内存：{flush}")
            else:
                logger.info(
                    f"发送失败",
                    "发送图片",
                    event.user_id,
                    getattr(event, "group_id", None),
                )
                await quotations.finish(f"发生错误！")
                flush = gc.collect()
                print(f"已清理内存：{flush}")

        elif DrawRegex:
            try:
                MaxCount = MaxDrawCountLoad[f"{event.group_id}"]
            except:
                MaxDrawCountLoad[f"{event.group_id}"] = 50
                MaxCount = 50
                with open(MainConfigPath,'w',encoding='utf-8') as f:
                    yaml.dump(MaxDrawCountLoad, f)
                await quotations.send("未配置抽卡上限，已默认配置为50发！")
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

            msg_list = []
            card_n, card_r, card_sr, card_ssr = 0, 0, 0, 0
            DatabaseDict = {"N": 0,"R": 0, "SR": 0, "SSR": 0}

            for i in range(int(DrawCount)):
                text = (await AsyncHttpx.get(url, timeout=10)).json()
                card = ""
                if text["from_who"] in n:
                    card = " | N卡"
                    card_n += 1
                    CountList["n"] += 1
                    DatabaseDict["N"] = DatabaseDict["N"] + 1
                else:
                    card_n
                if text["from_who"] in r:
                    card = " | R卡"
                    card_r += 1
                    CountList["r"] += 1
                    DatabaseDict["R"] = DatabaseDict["R"] + 1
                else:
                    card_r
                if text["from_who"] in sr:
                    card = " | SR卡"
                    card_sr += 1
                    CountList["sr"] += 1
                    DatabaseDict["SR"] = DatabaseDict["SR"] + 1
                else:
                    card_sr
                if text["from_who"] in ssr:
                    card = " | SSR卡"
                    card_ssr += 1
                    CountList["ssr"] += 1
                    DatabaseDict["SSR"] = DatabaseDict["SSR"] + 1
                else:
                    card_ssr
                if text["from_who"] not in CardPool:
                    card = ""
                if datetime.datetime.now() < EndTime:
                    if text["from_who"] in ['晨于曦Asahi', '冰蓝IceBlue', '晨宝的老公']:
                        card = " | UR卡"
                data = {
            "type": "node",
            "data": {"name": "楠桐语录", "uin": f"{bot.self_id}", "content": f'〔g{text["id"]}〕 {text["hitokoto"]} | {text["from_who"]}{card}'},
        }
                msg_list.append(data)

            with open(CardCountPath,'w',encoding='utf-8') as f:
                json.dump(CountList, f,ensure_ascii=False)
            if db.check(str(event.user_id)) != []:
                db.uptate(event.user_id, CountDict=DatabaseDict)
            else:
                db.write(event.user_id, event.group_id)
                db.uptate(event.user_id, CountDict=DatabaseDict)
            result = {
            "type": "node",
            "data": {"name": "楠桐语录", "uin": f"{bot.self_id}", "content": f"汇总：N：{card_n} R：{card_r} SR：{card_sr} SSR：{card_ssr}"},
        }
            msg_list.append(result)
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
            flush = gc.collect()
            print(f"已清理内存：{flush}")
        # elif UpPoolRegex:
        #     while True:
        #         break
        elif SentenceCheck in ["统计"]:
            if len(msg) >= 2:
                RegexNameCount = 0
                RegexAuthorCount = 0
                name = msg[1]
                for i in NameRegexList:
                    NameRegex = re.search(name, i)
                    if NameRegex:
                        RegexNameCount += 1
                for i in List:
                    for key,value in UserDict.items():
                        if key == name:
                            name = value
                    AuthorRegex = re.search(name, i)
                    if AuthorRegex:
                        RegexAuthorCount += 1
                RegexAllCount = int(RegexNameCount) + int(RegexAuthorCount)
                RegexPercent = float(int(RegexAllCount / len(content) * 10000) / 100)
                await quotations.finish(f"""目前楠桐语录中有{RegexNameCount}条语录与{msg[1]}有关，有{RegexAuthorCount}条语录作者包含{name}，合计{RegexAllCount}条，占比{RegexPercent}%。""")
            result = db.count(str(event.user_id))
            n, r, sr, ssr = 0, 0, 0, 0
            if result != []:
                result = result[0]
                n = result["N"]
                r = result["R"]
                sr = result["SR"]
                ssr = result["SSR"]

            CountJson = open(CardCountPath, 'r')
            c = CountJson.read()
            CountJson.close()
            CountList = json.loads(c)
            CardDict = {}
            DrawCount = CountList["n"] + CountList["r"] + CountList["sr"] + CountList["ssr"]

            await quotations.finish(f"""从2023年11月1日21点40分开始，您一共抽取了{n + r + sr + ssr}条语录
其中N卡{n}张，R卡{r}张，SR卡{sr}张，SSR卡{ssr}张""")

        else:
            await quotations.finish("参数有误,code:10404，请使用'帮助楠桐语录'查看帮助...")
            flush = gc.collect()
            print(f"已清理内存：{flush}")

    else:
        await quotations.finish("参数有误,code:10001，请使用'帮助楠桐语录'查看帮助...")
        flush = gc.collect()
        print(f"已清理内存：{flush}")