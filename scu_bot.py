from nonebot import on_command
from services.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.params import CommandArg


__zx_plugin_name__ = "上传语录"
__plugin_usage__ = """
usage：
    上传语录
    指令：
        上传语录 语录名称 语录内容
        上传语录 语录名称 语录内容 语录作者（目前仅限楠桐语录需要填写作者）
        例：上传语录 桑吉 人家45
        例：上传语录 楠桐 我是楠桐 晨于曦Asahi
""".strip()
__plugin_des__ = "上传语录"
__plugin_cmd__ = ["上传语录"]
__plugin_version__ = 1.0
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["上传语录"],
}
__plugin_type__ = ("语录", 1)


UploadSentece = on_command("上传语录", aliases={"上传语录"}, priority=5, block=True)

@UploadSentece.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await UploadSentece.finish("参数不完全，请查看订阅帮助...")
    SentenceName = msg[0]
    
    result = f'已成功将{author}说的{sentence}上传至{SentenceName}语录'
    await UploadSentece.send(result)
    logger.info(
        f"(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else 'private'}) 上传语录:"
        + result
    )