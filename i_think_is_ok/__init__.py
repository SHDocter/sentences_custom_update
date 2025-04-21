from nonebot import on_keyword, on_message, on_notice, require, get_driver, on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent
from utils.message_builder import image
from utils.http_utils import AsyncHttpx
from configs.path_config import TEMP_PATH
from utils.image_utils import get_img_hash
from configs.config import Config
from configs.path_config import IMAGE_PATH
from utils.utils import get_message_text, get_message_img, get_bot, scheduler
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Event, GroupRecallNoticeEvent, FriendRecallNoticeEvent, Message, MessageEvent
from nonebot.params import CommandArg
from pathlib import Path
import os
import gc
import re
import json
import random
import asyncio

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

__plugin_configs__ = {
    "I_THINK_RANDOM_MODE": {
        "value": 6,
        "help": "是否启用随机发送楠桐语录",
        "default_value": True,
        "type": float,
    }
}

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
random_mode = on_command("彩蛋", aliases={}, priority=5, block=True)

ImagePath = IMAGE_PATH / "scu/easter_egg"
ResourcesPath = Path() / "custom_plugins" / "i_think_is_ok"
ImgPath = ResourcesPath / "img"
GroupListPath = ResourcesPath / "group_list.json"
UserListPath = ResourcesPath / "user_list.json"
RandomModePath = ResourcesPath / "random_mode.json"
PercentPath = ResourcesPath / "percent.json"

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

if not RandomModePath.exists():
    with open(RandomModePath, "w", encoding="utf-8") as rm:
        ModeList = {
            "group_id": True
        }
        json.dump(ModeList, rm, ensure_ascii=False, indent=4)

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
        #         logger.info(f"已成功清理内存：{flush}")
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
                logger.info(f"已成功清理内存：{flush}")
        if re.search("傲娇", str(event.message)):
            length = len(os.listdir(ImagePath))
            if length == 0:
                logger.warning(f"彩蛋图库为空，调用取消！")
                await send_img.finish("哥们没活了呜呜呜")
            result = image("scu/easter_egg/" + "1.gif")
            await send_img.send(result)
            flush = gc.collect()
            logger.info(f"已成功清理内存：{flush}")

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
#         logger.info(f"已成功清理内存：{flush}")
#     else:
#         print("debug:false")
#         pass

@fudu.handle()
async def _(event: GroupMessageEvent):
    init = 0.15
    percent = random.random()
    with open(GroupListPath, "r", encoding="utf-8") as gl:
        GroupList = json.load(gl)
    with open(RandomModePath, "r", encoding="utf-8") as rm:
        random_mode_list = json.load(rm)
    if f"{event.group_id}" in GroupList and f"{event.group_id}" not in random_mode_list:
        random_mode_list[str(event.group_id)] = True
        with open(RandomModePath, "w+", encoding="utf-8") as rm:
            json.dump(random_mode_list, rm, ensure_ascii=False, indent=4)
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
        if Config.get_config("i_think_is_ok", "I_THINK_RANDOM_MODE") and f"{event.group_id}" in GroupList and random_mode_list[str(event.group_id)]:
            save_percent(event.group_id)

        _fudu_list.clear(event.group_id)
        _fudu_list.append(event.group_id, add_msg)

    if _fudu_list.size(event.group_id) == 2:
        if percent <= init and not _fudu_list.is_repeater(event.group_id):
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
                _fudu_list.clear(event.group_id)
                await fudu.finish(rst)
                flush = gc.collect()
                logger.info(f"已成功清理内存：{flush}")
        elif percent >= init and percent <= 0.45 and not _fudu_list.is_repeater(event.group_id):
            if Config.get_config("i_think_is_ok", "I_THINK_RANDOM_MODE") and f"{event.group_id}" in GroupList and random_mode_list[str(event.group_id)] and not _fudu_list.is_repeater(event.group_id):
                _fudu_list.set_repeater(event.group_id)
                url = "https://ana.nya-wsl.cn/nicegui/ana/gay/json"
                data = (await AsyncHttpx.get(url, timeout=5)).json()
                _fudu_list.clear(event.group_id)
                await fudu.finish(f'{data["author"]}：{data["msg"]}')
                flush = gc.collect()
                logger.info(f"已成功清理内存：{flush}")
            else:
                logger.info("不符合条件，跳过复读...")
        else:
            logger.info("跳过复读...")
        # else:
        #     await fudu.finish(image("scu/easter_egg/" + "fudu.jpg"))
        #     flush = gc.collect()
        #     print(f"已成功清理内存：{flush}")
    if _fudu_list.size(event.group_id) > 2:
        if load_percent(event.group_id) != "":
            up_percent = float(load_percent(event.group_id))
        else:
            up_percent = float(f"0.{_fudu_list.size(event.group_id)}")
        if percent <= 0.1 + up_percent and not _fudu_list.is_repeater(event.group_id):
            _fudu_list.set_repeater(event.group_id)
            if Config.get_config("i_think_is_ok", "I_THINK_RANDOM_MODE") and f"{event.group_id}" in GroupList and random_mode_list[str(event.group_id)]:
                url = "https://ana.nya-wsl.cn/nicegui/ana/gay/json"
                data = (await AsyncHttpx.get(url, timeout=5)).json()
                _fudu_list.clear(event.group_id)
                await fudu.finish(f'{data["author"]}：{data["msg"]}')
                flush = gc.collect()
                logger.info(f"已成功清理内存：{flush}")
            else:
                if img and msg:
                    rst = msg + image(TEMP_PATH / f"fudu_{event.group_id}.jpg")
                elif img:
                    rst = image(TEMP_PATH / f"fudu_{event.group_id}.jpg")
                elif msg:
                    rst = msg
                else:
                    rst = ""
                if rst:
                    _fudu_list.clear(event.group_id)
                    await fudu.finish(rst)
                    flush = gc.collect()
                    logger.info(f"已成功清理内存：{flush}")
        else:
            logger.info(f"跳过复读...当前概率：{_fudu_list.size(event.group_id)}0%")

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

def save_percent(group_id):
    if os.path.exists(PercentPath):
        with open(PercentPath, "r", encoding="utf-8") as f:
            save_percent = json.load(f)
    else:
        save_percent = {}

    with open(PercentPath, "w+", encoding="utf-8") as f:
        save_percent[str(group_id)] = float(_fudu_list.size(group_id)) / 10
        json.dump(save_percent, f, ensure_ascii=False, indent=4)

def load_percent(group_id):
    if os.path.exists(PercentPath):
        with open(PercentPath, "r", encoding="utf-8") as f:
            load_percent = json.load(f)
    else:
        load_percent = {}

    return load_percent[str(group_id)]

@random_mode.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    with open(RandomModePath, "r", encoding="utf-8") as rm:
        random_mode_list = json.load(rm)
    msg = arg.extract_plain_text().strip().split()
    if msg[0] == "随机模式":
        if msg[1] == "开启":
            random_mode_list[str(event.group_id)] = True
            with open(RandomModePath, "w+", encoding="utf-8") as rm:
                json.dump(random_mode_list, rm, ensure_ascii=False, indent=4)
            await random_mode.finish("随机回复楠桐语录已开启")
        if msg[1] == "关闭":
            random_mode_list[str(event.group_id)] = False
            with open(RandomModePath, "w+", encoding="utf-8") as rm:
                json.dump(random_mode_list, rm, ensure_ascii=False, indent=4)
            await random_mode.finish("随机回复楠桐语录已关闭")

# message_back = on_notice(rule=handle_rule, priority=50)

# @scheduler.scheduled_job(
#     "cron",
#     year=2024,
#     month=12,
#     day=31,
#     hour=23,
#     minute=55,
# )
# async def _():
#     bot = get_bot()
#     await bot.send_group_msg(group_id="932044296", message="马上就是2025年了，感恩大家2024年对我的忽视，我很喜欢这个群，大家都各聊各的，没人鸟我 我也不想鸟你们，很温馨的一个圈子，我很欣慰。我删了很多群，唯独你们舍不得删，因为大家都展现出真实的自己，色情 装逼 矫情 贪婪 伪善 两面三刀 笑里藏刀 道貌岸然 自私 虚荣 狡诈 虚伪 冷漠 龌龊 卑鄙 见利忘义 嫌贫爱富 厚颜无耻 阴阳怪气。希望大家继续加油 我会一直和你们耗下去 你们这群叼毛。")
#     await asyncio.sleep(60)
#     await bot.send_group_msg(group_id="932044296", message="大过年的，不会还有人加班吧？哥们儿提前下班辣！明年见叼毛们")
#     await bot.send_group_msg(group_id="932044296", message="@小丑竟是我自己")
#     os.system("pm2 stop bot")

# @scheduler.scheduled_job(
#     "cron",
#     year=2025,
#     month=1,
#     day=1,
#     hour=8,
# )
# async def _():
#     bot = get_bot()
#     await bot.send_group_msg(group_id="932044296", message="早上好，楠桐们！今天的加班乐透，最后结果是满打满算的整整十二小时！")

@scheduler.scheduled_job(
    "cron",
    day_of_week=6,
    hour=23,
    minute=59,
)
async def _():
    bot = get_bot()
    await bot.send_group_msg(group_id="932044296", message=image("scu/easter_egg/" + "每周礼包.jpg"))