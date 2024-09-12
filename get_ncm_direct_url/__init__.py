from nonebot import on_command #type: ignore
from nonebot.params import CommandArg #type: ignore
from nonebot.adapters.onebot.v11 import Message #type: ignore

from pyncm import apis

__zx_plugin_name__ = "获取网易云音乐直链"
__plugin_cmd__ = ["ncm"]
__plugin_version__ = 0.1
__plugin_author__ = "Nya-WSL"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["网易云", "ncm", "NCM"],
}
__plugin_usage__ = """
usage：
    目前支持使用游客账号并通过pc端接口获取链接
    如果是vip歌曲，会返回试听时长

    指令：
    网易云/ncm[NCM] 歌曲id
""".strip()

GetNcmInfo = on_command("网易云", aliases={"ncm", "NCM"}, priority=5, block=True)

@GetNcmInfo.handle()
async def _(arg: Message = CommandArg()):
    apis.login.LoginViaAnonymousAccount() # 匿名登录ncm
    msg = arg.extract_plain_text().strip().split()
    if msg == []:
        await GetNcmInfo.finish("请输入正确的歌曲id")
    else:
        song_id = msg[0]
        song_info = apis.track.GetTrackAudio(song_ids=song_id)
        result = ""
        if song_info["data"][0]["freeTrialInfo"] == None:
            result = f"id：{song_info['data'][0]['id']}\n链接：{song_info['data'][0]['url']}\n后缀：{song_info['data'][0]['type']}\nVIP：是"
        else:
            result = f"id：{song_info['data'][0]['id']}\n链接：{song_info['data'][0]['url']}\nVIP：是\n试听：{song_info['data'][0]['freeTrialInfo']['end']}秒\n"

        await GetNcmInfo.finish(result)