import os
import json
import uuid
import datetime
from nonebot import on_command
from services.log import logger
# from configs.config import Config
from nonebot.typing import T_State
from nonebot.params import CommandArg
from utils.utils import get_message_img
from utils.http_utils import AsyncHttpx
# from models.level_user import LevelUser
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent


__zx_plugin_name__ = "上传语录"
__plugin_usage__ = """
usage：
    上传语录
    指令：
        上传语录 语录名称 语录内容
        上传语录 语录名称 语录内容 语录作者（目前仅限楠桐语录和语录合集需要填写作者）
        上传图片 语录名称 [图片]
        
        语录内容不能有空格
        图片不需要填写作者
        图片暂不支持使用回复
        
        例：上传语录 桑吉/桑吉语录 人家45
        例：上传语录 楠桐/楠桐语录 我是楠桐 晨于曦Asahi
        例：上传图片 楠桐 [图片]
""".strip()
__plugin_des__ = "上传语录"
__plugin_cmd__ = ["上传语录"]
__plugin_version__ = "1.0.5"
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["上传语录","上传图片"],
}
__plugin_type__ = ("语录", 1)

__plugin_configs__ = {
    "SCU_GROUP_LEVEL": {
        "value": 5,
        "help": "群内上传语录需要的权限",
        "default_value": 5,
        "type": int,
    },
}

UploadSentence = on_command("上传语录", aliases={"上传语录"}, priority=5, block=True)
up_img = on_command("上传图片", aliases={"上传图片"}, priority=5, block=True)

@UploadSentence.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    global SentenceName
    global sentence
    global author
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await UploadSentence.finish("参数不完全，请使用'！帮助上传语录'查看帮助...")
    # if isinstance(event, GroupMessageEvent):
    #     if not await LevelUser.check_level(
    #         event.user_id,
    #         event.group_id,
    #         Config.get_config("scu_bot", "SCU_GROUP_LEVEL"),
    #     ):
    #         await UploadSentence.finish(
    #             f"您的权限不足，上传语录需要 {Config.get_config('scu_bot', 'SCU_GROUP_LEVEL')} 级权限..",
    #             at_sender=False
    #         )
    SentenceName = msg[0]
    sentence = msg[1]
    if SentenceName in ["楠桐","语录","楠桐语录","语录合集"]:
        try:
            author = msg[2]
        except:
            await UploadSentence.finish("作者获取异常！")

    if SentenceName in ["桑吉","羽月","楠桐","小晨","语录","桑吉语录","羽月语录","楠桐语录","小晨语录","语录合集"]:
        if SentenceName in ["楠桐","楠桐语录","语录","语录合集"]:
            if SentenceName in ["楠桐","语录"]:
                result = f'已成功将{author}说的{sentence}上传至{SentenceName}语录'
            else:
                result = f'已成功将{author}说的{sentence}上传至{SentenceName}'
        else:
            if SentenceName in ["桑吉","羽月","小晨"]:
                result = f'已成功将{sentence}上传至{SentenceName}语录'
            else:
                result = f'已成功将{sentence}上传至{SentenceName}'
    else:
        await UploadSentence.finish("该语录不存在！")

    try:
        Upload()
        cmd = "/root/hitokoto-api/restart.sh"
        os.system(cmd)
        result_id = result + f" id:{id}"
        await UploadSentence.send(result_id)
    except:
        await UploadSentence.finish("发生错误！")
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 上传语录:"
        + result
    )

up_img = on_command("上传图片", aliases={"上传图片"}, priority=5, block=True)

ScuPath = "/home/zhenxun_bot-main/resources/image/scu/"

@up_img.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    # if isinstance(event, GroupMessageEvent):
    #     if not await LevelUser.check_level(
    #         event.user_id,
    #         event.group_id,
    #         Config.get_config("scu_bot", "SCU_GROUP_LEVEL"),
    #     ):
    #         await UploadSentence.finish(
    #             f"您的权限不足，上传语录需要 {Config.get_config('scu_bot', 'SCU_GROUP_LEVEL')} 级权限..",
    #             at_sender=False
    #     )
    img = get_message_img(event.json())
    msg = arg.extract_plain_text().strip().split()
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
    if not await AsyncHttpx.download_file(
        img, ScuImgPath + f"{event.user_id}_scu_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
    ):
        await up_img.finish("上传图片失败...请稍后再试...")

    await up_img.send("已成功上传图片")
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'})"
        f" 已成功上传图片"
    )

def Upload():
    global id
    path = "/scu/" # 语录的路径
    SentencesFile = "" # 留空

    if SentenceName in ["桑吉","桑吉语录"]:
        SentencesFile = path + "a.json" # 语录文件
    elif SentenceName in ["羽月","羽月语录"]:
        SentencesFile = path + "b.json"
    elif SentenceName in ["楠桐","楠桐语录"]:
        SentencesFile = path + "c.json"
    elif SentenceName in ["小晨","小晨语录"]:
        SentencesFile = path + "d.json"
    elif SentenceName in ["语录","语录合集"]:
        SentencesFile = path + "e.json"
    else:
        UploadSentence.finish("该语录不存在！")

    item_dict = "" # 留空
    f = open(SentencesFile, 'r', encoding="utf-8") # 将语言文件写入缓存
    text = f.read() # 读取语言
    f.close() # 关闭语言文件
    content = json.loads(text) # 转为List，List中为字典
    id = len(content) + 1 # 获取字典位数并加1的方式自动更新id
    Uuid = str(uuid.uuid4()) # 基于随机数生成uuid，可能会有极小的概率重复
    if SentenceName in ["桑吉","桑吉语录"]:
        item_dict = {
    "id": f"{id}", # 新的id，通过此方式写入双引号
    "uuid": f"{Uuid}", # 新的uuid，通过此方式写入双引号
    "hitokoto": f"{sentence}", # 需要添加的语录将填入这里，通过此方式写入双引号
    "type": "a",
    "from": "资本家聚集地",
    "from_who": "桑吉Sage",
    "creator": "桑吉Sage",
    "creator_uid": "1",
    "reviewer": "1",
    "commit_from": "web",
    "created_at": "1626590063",
    "length": "19"
} # 需添加的对象
    elif SentenceName in ["羽月","羽月语录"]:
        item_dict = {
    "id": f"{id}",
    "uuid": f"{Uuid}",
    "hitokoto": f"{sentence}",
    "type": "b",
    "from": "羽月ちい",
    "from_who": "羽月ちい",
    "creator": "羽月ちい",
    "creator_uid": "1",
    "reviewer": "1",
    "commit_from": "web",
    "created_at": "1626590063",
    "length": "19"
}
    elif SentenceName in ["楠桐","楠桐语录"]:
        item_dict = {
    "id": f"{id}",
    "uuid": f"{Uuid}",
    "hitokoto": f"{sentence}",
    "type": "c",
    "from": f"{author}", # 填入作者，通过此方式写入双引号
    "from_who": f"{author}",
    "creator": f"{author}",
    "creator_uid": "1",
    "reviewer": "1",
    "commit_from": "web",
    "created_at": "1626590063",
    "length": "19"
}
    elif SentenceName in ["小晨","小晨语录"]:
        item_dict = {
    "id": f"{id}",
    "uuid": f"{Uuid}",
    "hitokoto": f"{sentence}",
    "type": "d",
    "from": "晨于曦Asahi",
    "from_who": "晨于曦Asahi",
    "creator": "晨于曦Asahi",
    "creator_uid": "1",
    "reviewer": "1",
    "commit_from": "web",
    "created_at": "1626590063",
    "length": "19"
}
    elif SentenceName in ["语录","语录合集"]:
        item_dict = {
    "id": f"{id}",
    "uuid": f"{Uuid}",
    "hitokoto": f"{sentence}",
    "type": "e",
    "from": f"{author}", # 填入作者，通过此方式写入双引号
    "from_who": f"{author}",
    "creator": f"{author}",
    "creator_uid": "1",
    "reviewer": "1",
    "commit_from": "web",
    "created_at": "1626590063",
    "length": "19"
}
    content.append(item_dict) # 将字典追加入列表

    with open(SentencesFile, 'w', encoding="utf-8") as JsonFile:
        json.dump(content, JsonFile, indent=4, ensure_ascii=False) # 打开并写入json中，保持4格缩进并避免中文乱码