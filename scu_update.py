import os
import sys
import time
import datetime
from urllib import request

workDir = os.getcwd() + "\\logs"
if not os.path.exists("logs"):
    os.mkdir(workDir)

# 错误处理
class Mylogpetion():
    def __init__(self):
        import traceback
        import logging
# logging的基本配置
        errorTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')  # 获取错误时间
        logging.basicConfig(
            filename=f'{workDir}\\update_debug_{errorTime}.txt',              # 当前文件写入位置
            format='%(asctime)s %(levelname)s \n %(message)s',             # 格式化存储的日志格式
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
# 写入日志
        logging.debug(traceback.format_exc())

try:
    UpdateUrl = "https://qn.nya-wsl.cn/scu/scu_remote_setup.exe" # 获取更新包url

# 百分比进度条
    def report(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\r%5.1f%% %*d / %d" % (percent, len(str(totalsize)), readsofar, totalsize)
            sys.stderr.write(s)
            if readsofar >= totalsize:
                sys.stderr.write("\n")
        else:
            sys.stderr.write("read %d\n" % (readsofar,))

    print("正在停止scu_remote...")
    os.system("taskkill /F /IM scu_remote.exe")
    time.sleep(2)
    if os.path.exists("scu_remote.exe"):
        os.remove("scu_remote.exe")
        time.sleep(2)
    else:
        print("本地未发现scu_remote.exe存在，即将跳过删除强制更新")
    print("正在下载更新...")
    request.urlretrieve(UpdateUrl,"scu_remote_setup.exe",report) # 下载更新包
    os.system("scu_remote_setup.exe")
    if os.path.exists("scu_remote_setup.exe"):
        print("正在删除安装程序...")
        os.remove("scu_remote_setup.exe")
    sys.exit("update is successful")
except:
    Mylogpetion() # 输出log