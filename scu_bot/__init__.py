import os
import re
import json
import fnmatch
import datetime
from qiniu import Auth, put_file, etag
from nonebot import on_command
from services.log import logger
from configs.config import Config
from nonebot.params import CommandArg
from utils.message_builder import image
from utils.utils import get_message_img, get_message_text
from utils.http_utils import AsyncHttpx
from configs.path_config import DATA_PATH, IMAGE_PATH
from models.level_user import LevelUser
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent

__zx_plugin_name__ = "上传语录"
__plugin_usage__ = """
usage：
    上传语录
    指令：
        上传语录 语录名称 语录内容
        [回复] 上传语录 语录名称 语录作者（如不填写作者将默认为群名称）
        上传语录 语录名称 语录内容 语录作者（目前仅限楠桐语录和语录合集需要填写作者）
        上传图片 语录名称 [图片] | [回复] 上传图片 语录名称
        上传语录 字典 作者（保存在语录中的名字） 别名 该命令将会为指定的作者添加一个别名 | [回复] 上传语录 字典 作者 该命令将会把回复的人的群id作为别名
        上传语录 字典 查询
        上传语录 黑名单 添加/删除 作者/别名 在黑名单的id将无法上传至语录，默认6级权限（注：指这个id无法被上传至语录，而不是这个id不能上传语录）
        上传语录 黑名单 查询
        查询语录
        还原语录 语录名称 | 该命令会将语录库还原到上传最后一条语录之前
        撤回语录 语录名称 撤回次数（如果没有撤回次数将撤回1次）
        提取语录 语录名称 语录作者（如果是不需要作者的语录该参数可以省略）| 支持字典
        
        语录内容不能有空格 | 图片不需要填写作者 | 回复作者不是必填的，默认为群名称
        还原语录功能的原理是恢复上传时的备份而不是删除元素，所以无论使用几次，都只会还原到上传最后一条语录之前
        语录库中后缀为.restore的文件为还原的文件；后缀为.restore.1的文件为还原前的文件；后缀为.revert的文件为撤回前的文件，撤回的备份最大数量可在bot的config中配置
        还原和撤回的区别：还原只能还原到上传最后一条语录前，无论运行多少次都是这样；撤回可以指定撤回次数并可以一直撤回到语录库为空，后续版本或许可以支持撤回指定的某一条语录
        6级权限需要管理员手动授权
        
        例：上传语录 桑吉/桑吉语录 人家45
        例：上传语录 楠桐/楠桐语录 我是楠桐 晨于曦Asahi
        例：[回复] 上传语录 楠桐 晨于曦Asahi
        例：上传图片 楠桐 [图片] | [回复] 上传图片 楠桐
        例：上传语录 字典 晨于曦Asahi 小晨 | [回复] 上传语录 字典 桑吉Sage
        例：还原语录 楠桐
""".strip()
__plugin_des__ = "上传语录"
__plugin_cmd__ = ["上传语录"]
__plugin_version__ = "1.2.3"
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["上传语录","上传图片","查询语录"],
}
__plugin_type__ = ("语录", 1)

__plugin_configs__ = {
    "SCU_GROUP_LEVEL": {
        "value": 5,
        "help": "群内部分语录功能需要的权限",
        "default_value": 5,
        "type": int,
    },
    "SCU_BLACKLIST_LEVEL": {
        "value": 6,
        "help": "群内调整黑名单需要的权限",
        "default_value": 6,
        "type": int,
    },
    "SCU_REVERT_LEVEL": {
        "value": 6,
        "help": "群内撤回语录需要的权限",
        "default_value": 6,
        "type": int,
    },
    "SCU_REVERT_COUNT": {
        "value": 10,
        "help": "群内撤回语录备份的最大数量",
        "default_value": 10,
        "type": int,
    }
}

ScuDataPath = DATA_PATH / "scu"
ScuImagePath = IMAGE_PATH / "scu"
UserDictPath = ScuDataPath / "user_dict.json"
BlackListPath = ScuDataPath / "blacklist.json"
ScuPath = "/home/zhenxun_bot-main/resources/image/scu/"

up_img = on_command("上传图片", aliases={"上传图片"}, priority=5, block=True)
UploadSentence = on_command("上传语录", aliases={"上传语录"}, priority=5, block=True)
CheckSentences = on_command("查询语录", aliases={"查询语录"}, priority=5, block=True)
RestoreSentence = on_command("还原语录", aliases={"还原语录"}, priority=5, block=True)
RevokeSentence = on_command("撤回语录", aliases={"撤回语录"}, priority=5, block=True)
ExtractSentnces = on_command("提取语录", aliases={"下载语录"}, priority=5, block=True)

if not os.path.exists(UserDictPath):
    with open(UserDictPath, "w", encoding="utf-8") as ud:
        ud.write(r"{}")
if not os.path.exists(BlackListPath):
    with open(BlackListPath, "w", encoding="utf-8") as blp:
        blp.write(r"[]")

@ExtractSentnces.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 1:
        await ExtractSentnces.finish("请选择语录！")
    path = "/var/www/ss-ana/data/"
    SentencesFile = ""
    if msg[0] in ["桑吉","桑吉语录"]:
        SentencesFile = path + "sage.json"
    elif msg[0] in ["羽月","羽月语录"]:
        SentencesFile = path + "chii.json"
    elif msg[0] in ["楠桐","楠桐语录"]:
        SentencesFile = path + "gay.json"
        if len(msg) < 2:
            await ExtractSentnces.finish("请选择作者！")
    elif msg[0] in ["小晨","小晨语录"]:
        SentencesFile = path + "asahi.json"
    elif msg[0] in ["语录","语录合集"]:
        SentencesFile = path + "collection.json"
        if len(msg) < 2:
            await ExtractSentnces.finish("请选择作者！")
    else:
        await ExtractSentnces.finish("提取的语录不存在！")
    f = open(SentencesFile, 'r', encoding="utf-8") # 将语言文件写入缓存
    sf = f.read() # 读取语言
    f.close() # 关闭语言文件
    SentencesList = json.loads(sf) # 转为List，List中为字典
    ExtractList = []
    with open(UserDictPath, "r", encoding="utf-8") as ud:
        UserDict = json.load(ud)
    author = ""
    time = datetime.datetime.now().strftime('%Y.%m.%d.%H%M')
    if len(msg) > 1:
        author = str(msg[1])
        for key,value in UserDict.items():
            if key == author:
                author = value
        FilePath = ScuDataPath / "cloud" / f"extract_{author}_{time}.json"
        for AuthorDict in SentencesList:
            if AuthorDict["author"] == author:
                ExtractList.append(AuthorDict["msg"])
        if ExtractList == []:
            await ExtractSentnces.finish("似乎没有这个人的语录")
        with open(FilePath, "w", encoding="utf-8") as f:
            json.dump(ExtractList, f, ensure_ascii=False, indent=0)
        if os.path.exists(FilePath):
            result = f"""提取{msg[0]}中的{author}完成！

下载地址：
https://cloud.nya-wsl.cn/pd/bot/extract_{author}_{time}.json

Powered by Nya-WSL Cloud
"""
            await ExtractSentnces.send(result)
        else:
            await ExtractSentnces.finish("提取语录发生错误！")
    else:
        FilePath = ScuDataPath / "cloud" / f"extract_{msg[0]}_{time}.json"
        for Dict in SentencesList:
            ExtractList.append(Dict["msg"])
        if ExtractList == []:
            await ExtractSentnces.finish("似乎没有这个人的语录")
        with open(FilePath, "w", encoding="utf-8") as f:
            json.dump(ExtractList, f, ensure_ascii=False, indent=0)
        if os.path.exists(FilePath):
            result = f"""提取{msg[0]}完成！

下载地址：
https://cloud.nya-wsl.cn/pd/bot/extract_{author}_{time}.json

Powered by Nya-WSL Cloud
"""
            await ExtractSentnces.send(result)
        else:
            await ExtractSentnces.finish("提取语录发生错误！")

@CheckSentences.handle()
async def _():
    SentencesList = "桑吉语录 羽月语录 楠桐语录 小晨语录 语录合集"
    result = f"已收录语录：{SentencesList}"
    await CheckSentences.send(result)

@RestoreSentence.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if isinstance(event, GroupMessageEvent):
        if not await LevelUser.check_level(
            event.user_id,
            event.group_id,
            Config.get_config("scu_bot", "SCU_GROUP_LEVEL"),
        ):
            await RestoreSentence.finish(
                f"发生错误！code:1012{Config.get_config('scu_bot', 'SCU_GROUP_LEVEL')}",
                at_sender=False
            )
    if len(msg) < 1:
        await RestoreSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
    path = "/var/www/ss-ana/data/"
    SentencesFile = ""
    if msg[0] in ["桑吉","桑吉语录"]:
        SentencesFile = path + "sage.json"
    elif msg[0] in ["羽月","羽月语录"]:
        SentencesFile = path + "chii.json"
    elif msg[0] in ["楠桐","楠桐语录"]:
        SentencesFile = path + "gay.json"
    elif msg[0] in ["小晨","小晨语录"]:
        SentencesFile = path + "asahi.json"
    elif msg[0] in ["语录","语录合集"]:
        SentencesFile = path + "collection.json"
    else:
        await RestoreSentence.finish("还原的语录不存在！")

    try:
        os.system(f"cp -rf {SentencesFile} {SentencesFile}.restore.1")
        os.system(f"cp -rf {SentencesFile}.restore {SentencesFile}")
        backup()
    except:
        await RestoreSentence.finish("还原过程中出现未知错误！")

@RevokeSentence.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if isinstance(event, GroupMessageEvent):
        if not await LevelUser.check_level(
            event.user_id,
            event.group_id,
            Config.get_config("scu_bot", "SCU_REVERT_LEVEL"),
        ):
            await UploadSentence.finish(
                f"发生错误！code:1012{Config.get_config('scu_bot', 'SCU_REVERT_LEVEL')}",
                at_sender=False
            )
    if len(msg) < 1:
        await RevokeSentence.finish("请选择语录！")
    path = "/var/www/ss-ana/data/"
    SentencesFile = ""
    if msg[0] in ["桑吉","桑吉语录"]:
        SentencesFile = path + "sage.json"
    elif msg[0] in ["羽月","羽月语录"]:
        SentencesFile = path + "chii.json"
    elif msg[0] in ["楠桐","楠桐语录"]:
        SentencesFile = path + "gay.json"
    elif msg[0] in ["小晨","小晨语录"]:
        SentencesFile = path + "asahi.json"
    elif msg[0] in ["语录","语录合集"]:
        SentencesFile = path + "collection.json"
    else:
        await RevokeSentence.finish("撤回的语录不存在！")

    number = 1
    if len(msg) > 1:
        if not re.match(r"([0-9]+)", msg[1]):
            await RevokeSentence.finish("参数有误！您是否发送的不是数字？")
        else:
            number = int(msg[1])
    # try:
    FileList = fnmatch.filter(os.listdir(path), f"{SentencesFile.split('/')[-1]}.revert.*")
    BakNumber = len(FileList)
    if BakNumber >= int(Config.get_config('scu_bot', 'SCU_REVERT_COUNT')):
        os.remove(path + FileList[0])
    os.system(f"cp -rf {SentencesFile} {SentencesFile}.revert.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    f = open(SentencesFile, 'r', encoding="utf-8") # 将语言文件写入缓存
    sf = f.read() # 读取语言
    f.close() # 关闭语言文件
    SentencesList = json.loads(sf) # 转为List，List中为字典
    for _ in range(number):
        SentencesList.pop()
    with open(SentencesFile, "w", encoding="utf-8") as f:
        json.dump(SentencesList, f, indent=4, ensure_ascii=False)
    backup()
    await RevokeSentence.finish("撤回成功！")
    # except:
    #     await RevokeSentence.finish("撤回过程中出现未知错误！")

@UploadSentence.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    global SentenceName
    global sentence
    global author
    with open(UserDictPath, "r", encoding="utf-8") as ud:
        UserDict = json.load(ud)
    with open(BlackListPath, "r", encoding="utf-8") as blp:
        BlackList = json.load(blp)
    msg = arg.extract_plain_text().strip().split()
    SentenceName = msg[0]

    if SentenceName in ["黑名单"]:
        if msg[1] == "查询":
            result = f'当前黑名单：' + str(BlackList).replace("[", "").replace("]", "").replace("'", "").replace(",", "，")
            await UploadSentence.finish(result)
        if isinstance(event, GroupMessageEvent):
            if not await LevelUser.check_level(
                event.user_id,
                event.group_id,
                Config.get_config("scu_bot", "SCU_BLACKLIST_LEVEL"),
            ):
                await UploadSentence.finish(
                    f"发生错误！code:1012{Config.get_config('scu_bot', 'SCU_BLACKLIST_LEVEL')}",
                    at_sender=False
                )
        if len(msg) < 3:
            await UploadSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
        author = str(msg[2])
        for key,value in UserDict.items():
            if key == author:
                author = value
        if msg[1] == "添加":
            if author in BlackList:
                await UploadSentence.finish(f"{author}已存在！")
            else:
                BlackList.append(author)
                with open(BlackListPath, "w", encoding="utf-8") as blp:
                    json.dump(BlackList, blp, ensure_ascii=False)
                await UploadSentence.finish(f"以成功添加{author}至黑名单！")
        if msg[1] == "删除":
            if not author in BlackList:
                await UploadSentence.finish(f"黑名单中未找到{author}！")
            else:
                BlackList.remove(author)
                with open(BlackListPath, "w", encoding="utf-8") as blp:
                    json.dump(BlackList, blp, ensure_ascii=False)
                await UploadSentence.finish(f"以成功将{author}从黑名单中删除！")
    if SentenceName in ["字典"]:
        if len(msg) > 1:
            if msg[1] in ["查询"]:
                result = str(UserDict).replace("{", "").replace("}", "").replace(":", " = ").replace("'", "").replace(", ", "\n")
                if result == "":
                    result = "当前字典为空！"
                await UploadSentence.finish(result)
        if event.reply:
            if len(msg) < 2:
                await UploadSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
            reply = json.loads(event.reply.json())
            user_key = msg[1]
            UserDict[f'{reply["sender"]["nickname"]}'] = user_key
            with open(UserDictPath, "w", encoding="utf-8") as ud:
                json.dump(UserDict, ud, ensure_ascii=False)
            await UploadSentence.finish(f'已成功将 {reply["sender"]["nickname"]} = {user_key} 添加至字典！')
        else:
            if len(msg) < 3:
                await UploadSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
            user_key = msg[1]
            user_value = msg[2]
            UserDict[f"{user_value}"] = user_key
            with open(UserDictPath, "w", encoding="utf-8") as ud:
                json.dump(UserDict, ud, ensure_ascii=False)
            await UploadSentence.finish(f"已成功将 {user_key} = {user_value} 添加至字典！")
    text = {"user_id": f"{event.user_id}"}
    if not os.path.exists("custom_plugins/scu_bot/user.json"):
        with open("custom_plugins/scu_bot/user.json", "w", encoding="utf-8") as u:
            json.dump(text, u, ensure_ascii=False)
    if not os.path.exists("custom_plugins/scu_bot/count.txt"):
        with open("custom_plugins/scu_bot/count.txt", "w") as t:
            t.write("0")
    with open("custom_plugins/scu_bot/user.json", "r", encoding="utf-8") as u:
        user = json.load(u)
    if f"{event.user_id}" == user["user_id"]:
        with open("custom_plugins/scu_bot/count.txt", "r") as t:
            count = int(t.read())
        if int(count) <= 1:
            count += 1
            with open("custom_plugins/scu_bot/count.txt", "w") as t:
                t.write(str(count))
        if int(count) >= 2:
            result = image("scu/1.jpg")
            print("debug")
            await UploadSentence.send(result)
            os.remove("custom_plugins/scu_bot/count.txt")
            os.remove("custom_plugins/scu_bot/user.json")
    else:
        os.remove("custom_plugins/scu_bot/count.txt")
        os.remove("custom_plugins/scu_bot/user.json")
        with open("custom_plugins/scu_bot/user.json", "w", encoding="utf-8") as u:
            json.dump(text, u, ensure_ascii=False)
        with open("custom_plugins/scu_bot/count.txt", "w") as t:
            t.write("1")

    if event.reply:
        reply = json.loads(event.reply.json())
        OriginSentence = str(get_message_text(event.reply.json()))
        strinfo = re.compile(r"\s+")
        sentence = strinfo.sub(",", OriginSentence)
        if SentenceName in ["楠桐","语录","楠桐语录","语录合集"]:
            try:
                if len(msg) >= 2:
                    author = str(msg[1])
                    for key,value in UserDict.items():
                        if key == author:
                            author = value
                else:
                    author = reply["sender"]["nickname"]
                    for key,value in UserDict.items():
                        if key == author:
                            author = value
            except:
                await UploadSentence.finish("作者获取异常！")
            # if author == "小丑竟是我自己":
            #     author = "桑吉Sage"
            # elif author == "冰蓝艾思博录":
            #     author = "毕方"

        if SentenceName in ["桑吉","羽月","楠桐","小晨","语录","桑吉语录","羽月语录","楠桐语录","小晨语录","语录合集"]:
            if SentenceName in ["楠桐","楠桐语录","语录","语录合集"]:
                if SentenceName in ["楠桐","语录"]:
                    result = f'已成功将{author}说的{sentence}上传至{SentenceName}语录'
                else:
                    result = f'已成功将{author}说的{sentence}上传至{SentenceName}'
                with open(BlackListPath, "r", encoding="utf-8") as blp:
                    BlackList = json.load(blp)
                if author in BlackList:
                    result = f"{author}已被管理员封禁！"
                    await UploadSentence.finish(result)
            else:
                if SentenceName in ["桑吉","羽月","小晨"]:
                    result = f'已成功将{sentence}上传至{SentenceName}语录'
                else:
                    result = f'已成功将{sentence}上传至{SentenceName}'
        else:
            await UploadSentence.finish("该语录不存在！")

        try:
            upload()
            backup()
            result_id = result + f" id:{id}"
            await UploadSentence.send(result_id)
        except:
            await UploadSentence.finish("发生错误！")
        logger.info(
            f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 上传语录:"
            + result
        )

    elif not event.reply:
        if len(msg) < 2:
            await UploadSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
        sentence = msg[1]
        if SentenceName in ["楠桐","语录","楠桐语录","语录合集"]:
            try:
                author = msg[2]
                for key,value in UserDict.items():
                    if key == author:
                        author = value
            except:
                await UploadSentence.finish("作者获取异常！")

        if SentenceName in ["桑吉","羽月","楠桐","小晨","语录","桑吉语录","羽月语录","楠桐语录","小晨语录","语录合集"]:
            if SentenceName in ["楠桐","楠桐语录","语录","语录合集"]:
                if SentenceName in ["楠桐","语录"]:
                    result = f'已成功将{author}说的{sentence}上传至{SentenceName}语录'
                else:
                    result = f'已成功将{author}说的{sentence}上传至{SentenceName}'
                with open(BlackListPath, "r", encoding="utf-8") as blp:
                    BlackList = json.load(blp)
                if author in BlackList:
                    result = f"{author}已被管理员封禁！"
                    await UploadSentence.finish(result)
            else:
                if SentenceName in ["桑吉","羽月","小晨"]:
                    result = f'已成功将{sentence}上传至{SentenceName}语录'
                else:
                    result = f'已成功将{sentence}上传至{SentenceName}'
        else:
            await UploadSentence.finish("该语录不存在！")

        upload()
        backup()
        result_id = result + f" id:{id}"
        await UploadSentence.send(result_id)

@up_img.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    img = get_message_img(event.json())
    msg = arg.extract_plain_text().strip().split()
    if not event.reply:
        if not img or not msg:
            await up_img.finish(f"格式错误：\n" + __plugin_usage__)
        img = img[0]
    ImgName = msg[0]
    if ImgName in ["楠桐","楠桐语录"]:
        ScuImgPath = ScuPath + "gay/"
    elif ImgName in ["桑吉","桑吉语录"]:
        ScuImgPath = ScuPath + "sage/"
    elif ImgName in ["羽月","羽月语录"]:
        ScuImgPath = ScuPath + "chii/"
    elif ImgName in ["小晨","小晨语录"]:
        ScuImgPath = ScuPath + "asahi/"
    elif ImgName in ["语录","语录合集"]:
        ScuImgPath = ScuPath + "other/"
    else:
        await up_img.finish("该语录不存在！")
    if not event.reply:
        if not await AsyncHttpx.download_file(
            img, ScuImgPath + f"{event.user_id}_scu_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        ):
            await up_img.finish("上传图片失败...请稍后再试...")
    elif event.reply:
        ImgJson = get_message_img(event.reply.json())
        img = ImgJson[0]
        if not await AsyncHttpx.download_file(
            img, ScuImgPath + f"{event.user_id}_scu_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
    ):
            await up_img.finish("上传图片失败...请稍后再试...(回复错误)")

    await up_img.send("已成功上传图片")
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'})"
        f" 已成功上传图片"
    )

def upload():
    global id
    path = "/var/www/ss-ana/data/" # 语录的路径
    SentencesFile = "" # 留空

    if SentenceName in ["桑吉","桑吉语录"]:
        SentencesFile = path + "sage.json" # 语录文件
    elif SentenceName in ["羽月","羽月语录"]:
        SentencesFile = path + "chii.json"
    elif SentenceName in ["楠桐","楠桐语录"]:
        SentencesFile = path + "gay.json"
    elif SentenceName in ["小晨","小晨语录"]:
        SentencesFile = path + "asahi.json"
    elif SentenceName in ["语录","语录合集"]:
        SentencesFile = path + "collection.json"
    else:
        UploadSentence.finish("该语录不存在！")

    #os.system(f"chmod -R 666 {path}")
    os.system(f"cp -rf {SentencesFile} {SentencesFile}.restore")
    item_dict = "" # 留空
    f = open(SentencesFile, 'r', encoding="utf-8") # 将语言文件写入缓存
    text = f.read() # 读取语言
    f.close() # 关闭语言文件
    content = json.loads(text) # 转为List，List中为字典
    id = len(content) + 1 # 获取字典位数并加1的方式自动更新id
    time = str(datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    if SentenceName in ["桑吉","桑吉语录"]:
        item_dict = {
    "id": f"{id}",
    "msg": f"{sentence}",
    "author": "桑吉Sage",
    "time": f"{time}"
}
    elif SentenceName in ["羽月","羽月语录"]:
        item_dict = {
    "id": f"{id}",
    "msg": f"{sentence}",
    "author": "羽月ちい",
    "time": f"{time}"
}
    elif SentenceName in ["楠桐","楠桐语录"]:
        item_dict = {
    "id": f"{id}",
    "msg": f"{sentence}",
    "author": f"{author}", # 填入作者，通过此方式写入双引号
    "time": f"{time}"
}
    elif SentenceName in ["小晨","小晨语录"]:
        item_dict = {
    "id": f"{id}",
    "msg": f"{sentence}",
    "author": "晨于曦Asahi",
    "time": f"{time}"
}
    elif SentenceName in ["语录","语录合集"]:
        item_dict = {
    "id": f"{id}",
    "msg": f"{sentence}",
    "author": f"{author}", # 填入作者，通过此方式写入双引号
    "time": f"{time}"
}
    content.append(item_dict) # 将字典追加入列表

    with open(SentencesFile, 'w', encoding="utf-8") as JsonFile:
        json.dump(content, JsonFile, indent=4, ensure_ascii=False) # 打开并写入json中，保持4格缩进并避免中文乱码

def backup(): # 云备份
    qiniu_path = "custom_plugins/scu_bot/key.json" # 云备份配置文件

    if not os.path.exists(qiniu_path):
        logger.error("未找到云备份配置文件！")
    else:
        with open(qiniu_path, 'r', encoding="utf-8") as f:
            data = json.load(f)

        #需要填写你的 Access Key 和 Secret Key
        access_key = data["access_key"]
        secret_key = data["secret_key"]

        #构建鉴权对象
        q = Auth(access_key, secret_key)

        #要上传的空间
        bucket_name = data["bucket_name"]

        #上传后保存的文件名
        key = data["path"]

        #生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)

        #要上传文件的本地路径
        localfile = data["localfile"]

        ret, info = put_file(token, key, localfile, version='v1') 
        print(info)
        assert ret['key'] == key
        assert ret['hash'] == etag(localfile)
        logger.info("云备份成功！")