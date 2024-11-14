from nonebot import on_keyword, on_message, on_notice, require, get_driver
from services.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
from configs.path_config import TEMP_PATH
from utils.image_utils import get_img_hash
from configs.path_config import IMAGE_PATH
from utils.utils import get_message_text, get_message_img
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Event, GroupRecallNoticeEvent, FriendRecallNoticeEvent
from pathlib import Path
import os
import gc
import re
import json
import random

# require("nonebot_plugin_apscheduler")
# from nonebot_plugin_apscheduler import scheduler
# scheduler = scheduler

__zx_plugin_name__ = "我觉得行"
__plugin_cmd__ = ["我觉得行"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["我觉得行"],
}
__plugin_type__ = ("语录", 1)
__plugin_usage__ = """
usage：
    A：我觉得行
    bot：你行不了一点
    
install：
    只有group_list.json中存在的群才会触发，该文件初次运行将会自动生成
    除了我觉得行功能以外，其他用户限定功能发送人qq号或者id需要存在于user_list.json中相关的键的值（值可以是列表指定多个用户，也可以是字符串指定单个用户）才能触发
    打断复读功能仅受group_list限制不受用户限制
""".strip()

class Fudu:
    def __init__(self):
        self.data = {}

    def append(self, key, content):
        self._create(key)
        self.data[key]["data"].append(content)

    def clear(self, key):
        self._create(key)
        self.data[key]["data"] = []
        self.data[key]["is_repeater"] = False

    def size(self, key) -> int:
        self._create(key)
        return len(self.data[key]["data"])

    def check(self, key, content) -> bool:
        self._create(key)
        return self.data[key]["data"][0] == content

    def get(self, key):
        self._create(key)
        return self.data[key]["data"][0]

    def is_repeater(self, key):
        self._create(key)
        return self.data[key]["is_repeater"]

    def set_repeater(self, key):
        self._create(key)
        self.data[key]["is_repeater"] = True

    def _create(self, key):
        if self.data.get(key) is None:
            self.data[key] = {"is_repeater": False, "data": []}

_fudu_list = Fudu()

send_img = on_message(permission=GROUP, priority=999)
fudu = on_message(permission=GROUP, priority=999)

ImagePath = IMAGE_PATH / "scu/easter_egg"
ResourcesPath = Path() / "custom_plugins" / "i_think_is_ok"
ImgPath = ResourcesPath / "img"
GroupListPath = ResourcesPath / "group_list.json"
UserListPath = ResourcesPath / "user_list.json"

if not os.path.exists(ImagePath):
    os.mkdir(ImagePath)
    os.system(f"cp -rf {ImgPath}/* {ImagePath}")
else:
    os.system(f"cp -rf {ImgPath}/* {ImagePath}")

if not GroupListPath.exists():
    with open(GroupListPath, "w", encoding="utf-8") as gl:
        gl.write(r"[]")

if not UserListPath.exists():
    with open(UserListPath, "w", encoding="utf-8") as ul:
        UserList = {
        "yhm": ["0000000000"],
        "example": "example"
}
        json.dump(UserList, ul, ensure_ascii=False, indent=4)

@send_img.handle()
async def _(event: MessageEvent):
    with open(GroupListPath, "r", encoding="utf-8") as gl:
        GroupList = json.load(gl)
    # with open(UserListPath, "r", encoding="utf-8") as ul:
    #     UserList = json.load(ul)
    if f"{event.group_id}" in GroupList:
        # 用户限定功能1
        # if f"{event.user_id}" in UserList["yhm"]:
        #     if re.search("yhm", str(event.message)) or re.search("樱花妹", str(event.message)):
        #         ImgList = fnmatch.filter(os.listdir(ImagePath), "asahi*.*")
        #         RandomImg = random.choice(ImgList)
        #         result = image(ImagePath / RandomImg)
        #         await send_img.send(result)
        #         flush = gc.collect()
        #         print(f"已成功清理内存：{flush}")
        # 全局功能，不限用户
        # if f"{event.message}" == "我觉得行":
        if re.search("行", str(event.message)):
            if re.search("[我俺你您他她它ta]", str(event.message)) and re.search("觉得|寻思", str(event.message)) and not re.search("不", str(event.message)) or re.search("不*[我俺你您他她它ta]觉得行|不*[我俺你您他她它ta]寻思行", str(event.message)):
                length = len(os.listdir(ImagePath))
                if length == 0:
                    logger.warning(f"彩蛋图库为空，调用取消！")
                    await send_img.finish("哥们没活了呜呜呜")
                result = image("scu/easter_egg/" + "1.jpg")
                await send_img.send(result)
                flush = gc.collect()
                print(f"已成功清理内存：{flush}")
        if re.search("傲娇", str(event.message)):
            length = len(os.listdir(ImagePath))
            if length == 0:
                logger.warning(f"彩蛋图库为空，调用取消！")
                await send_img.finish("哥们没活了呜呜呜")
            result = image("scu/easter_egg/" + "1.gif")
            await send_img.send(result)
            flush = gc.collect()
            print(f"已成功清理内存：{flush}")

# @scheduler.scheduled_job(
#     "cron",
#     hour=0,
#     minute=1,
# )
# async def _():
#     print("debug:init")
#     if datetime.datetime.now().weekday() == 1:
#         with open(GroupListPath, "r", encoding="utf-8") as gl:
#             GroupList = json.load(gl)
#         driver = get_driver()
#         BOT_ID = str(driver.config.bot_id)
#         bot = driver.bots[BOT_ID]

#         print("debug:true")
#         length = len(os.listdir(ImagePath))
#         if length == 0:
#             logger.warning(f"彩蛋图库为空，调用取消！")
#         result = image("scu/easter_egg/" + "blhx.jpg")
#         for group_id in GroupList:
#             await bot.send_group_msg(
#                 group_id=group_id,
#                 message=result
#             )
#         flush = gc.collect()
#         print(f"已成功清理内存：{flush}")
#     else:
#         print("debug:false")
#         pass

@fudu.handle()
async def _(event: GroupMessageEvent):
    with open(GroupListPath, "r", encoding="utf-8") as gl:
        GroupList = json.load(gl)
    if f"{event.group_id}" in GroupList:
        if event.is_tome():
            return
        img = get_message_img(event.json())
        msg = get_message_text(event.json())
        if not img and not msg:
            return
        if img:
            img_hash = await get_fudu_img_hash(img[0], event.group_id)
        else:
            img_hash = ""
        add_msg = msg + "|-|" + img_hash
        if _fudu_list.size(event.group_id) == 0:
            _fudu_list.append(event.group_id, add_msg)
        elif _fudu_list.check(event.group_id, add_msg):
            _fudu_list.append(event.group_id, add_msg)
        else:
            _fudu_list.clear(event.group_id)
            _fudu_list.append(event.group_id, add_msg)
        if _fudu_list.size(event.group_id) >= 2:
            _fudu_list.clear(event.group_id)
            if random.random() <= 0.9 and not _fudu_list.is_repeater(event.group_id):
                _fudu_list.set_repeater(event.group_id)
                if img and msg:
                    rst = msg + image(TEMP_PATH / f"fudu_{event.group_id}.jpg")
                elif img:
                    rst = image(TEMP_PATH / f"fudu_{event.group_id}.jpg")
                elif msg:
                    rst = msg
                else:
                    rst = ""
                if rst:
                    await fudu.finish(rst)
                    flush = gc.collect()
                    print(f"已成功清理内存：{flush}")
            else:
                await fudu.finish(image("scu/easter_egg/" + "fudu.jpg"))
                flush = gc.collect()
                print(f"已成功清理内存：{flush}")

async def get_fudu_img_hash(url, group_id):
    try:
        if await AsyncHttpx.download_file(
            url, TEMP_PATH / f"fudu_{group_id}.jpg"
        ):
            img_hash = get_img_hash(TEMP_PATH / f"fudu_{group_id}.jpg")
            return str(img_hash)
        else:
            logger.warning(f"下载图片失败...")
    except Exception as e:
        logger.warning(f"图片Hash出错 {type(e)}：{e}")
    return ""

async def handle_rule(bot: Bot, event: Event) -> bool:
    if isinstance(event, GroupRecallNoticeEvent) or isinstance(event, FriendRecallNoticeEvent):
        return True
    return False

message_back = on_notice(rule=handle_rule, priority=50)

@message_back.handle()
async def message_back_handle(bot: Bot, Gevent: GroupRecallNoticeEvent):
    with open(GroupListPath, "r", encoding="utf-8") as gl:
        GroupList = json.load(gl)
    if f"{Gevent.group_id}" in GroupList:
        if Gevent.user_id == Gevent.operator_id:
            await bot.call_api('get_msg', **{"message_id": Gevent.message_id}) # 获取撤回的消息id
            result = image("scu/easter_egg/" + "2.jpg")
            await message_back.finish(result)