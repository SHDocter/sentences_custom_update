import os
import sys
import glob
import uuid
import json
import base64
import socket
import requests
import datetime
from icon import img
from tkinter import *
from urllib import request
import tkinter.messagebox as tkmb
from ftplib import FTP, error_perm

if os.path.exists("scu_update.exe"):
    os.remove("scu_update.exe")

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
            filename=f'{workDir}\\scu_debug_{errorTime}.txt',              # 当前文件写入位置
            format='%(asctime)s %(levelname)s \n %(message)s',             # 格式化存储的日志格式
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
# 写入日志
        logging.debug(traceback.format_exc())

def files(curr_dir = '.', ext = '*.json'):
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i

def RemoveFiles(dir, ext):
    for i in files(dir, ext):
        os.remove(i)

def UploadSuccessful():
    tkmb.showinfo(title="上传成功", message="上传完成，如上传出现问题请查看log或与我们联系 | 上传语录：" + JsonName + "语录")

def UploadSentence():
    global JsonName
    global SentencesFile
    url = "http://sentence.osttsstudio.ltd:9000/" # 语录的获取url，需自行修改web服务器配置，需保留末尾的“/”
    JsonUrl = "" # 留空
    SentencesFile = "" # 留空
    JsonName = SentenceJsonName.get()
    if JsonName == "桑吉":
        JsonUrl = url + "a.json" # 语录的获取url
        request.urlretrieve(JsonUrl,"a_local.json") # 下载语录到根目录
        SentencesFile = "a.json" # 更新后的语录文件名，建议与服务器上的文件名字保持一致
    elif JsonName == "羽月":
        JsonUrl = url + "b.json"
        request.urlretrieve(JsonUrl,"b_local.json")
        SentencesFile = "b.json"
    elif JsonName == "楠桐":
        JsonUrl = url + "c.json"
        request.urlretrieve(JsonUrl,"c_local.json")
        author = SentenceAuthor.get() # 获取作者
        SentencesFile = "c.json"
    else:
        SentenceNameError()

    sentence = SentenceText.get()
    if author == "":
        SentenceAuthorError()
    elif sentence == "":
        SentenceTextError()
    else:
        item_dict = "" # 留空
        OpenJsonFile = "" # 留空
        if JsonName == "桑吉":
            OpenJsonFile = "a_local.json" # 与上方request的文件名一致
        if JsonName == "羽月":
            OpenJsonFile = "b_local.json"
        if JsonName == "楠桐":
            OpenJsonFile = "c_local.json"
        f = open(OpenJsonFile, 'r', encoding="utf-8") # 将语言文件写入缓存
        text = f.read() # 读取语言
        f.close() # 关闭语言文件
        content = json.loads(text) # 转为List，List中为字典
        id = len(content) + 1 # 获取字典位数并加1的方式自动更新id
        Uuid = str(uuid.uuid4()) # 基于随机数生成uuid，可能会有极小的概率重复
        if JsonName == "桑吉":
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
        elif JsonName == "羽月":
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
        elif JsonName == "楠桐":
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
        content.append(item_dict) # 将字典追加入列表

        with open(SentencesFile, 'w', encoding="utf-8") as JsonFile:
            json.dump(content, JsonFile, indent=4, ensure_ascii=False) # 打开并写入json中，保持4格缩进并避免中文乱码

        host = '150.158.171.157'
        port = 21
        username = 'scu'
        password = '' # 脱敏

        ftp = FtpConnect(host, port, username, password)
        # 避免提示 ftplib.error_perm: 550 SIZE not allowed in ASCII
        ftp.voidcmd('TYPE I')
        UploadFile(ftp, SentencesFile) # 上传文件
        ftp.close()
        RemoveFiles('.', '*.json')
        UploadSuccessful()

def UpdateInfo():
    tkmb.showinfo(title="版本更新", message="检测到新版本！即将开始更新！")

def TestInfo():
    tkmb.showinfo(title="", message="该程序目前尚不完善，如有任何问题请与我们联系！")

def SentenceNameError():
    tkmb.showwarning(title="语录名称错误", message="该语录不存在，请检查！")

def SentenceTextError():
    tkmb.showwarning(title="语录错误", message="上传内容为空，请检查！")

def SentenceAuthorError():
    tkmb.showwarning(title="错误", message="作者为空，请检查！")

def FtpConnect(host, port, username, password):
    ftp = FTP()
    ftp.set_debuglevel(2) # 打开调试级别2，显示详细信息
    ftp.encoding = 'utf-8' # 解决中文编码问题，默认是latin-1
    try:
        ftp.connect(host, port)
        ftp.login(username, password)
        print(ftp.getwelcome()) # 打印欢迎信息
    except(socket.error, socket.gaierror): # 连接错误
        ConnectError = print("ERROR: cannot connect [{}:{}]" .format(host, port))
        ConnectError = f"ERROR: cannot connect [{host}:{port}]"
        sys.exit(ConnectError)
    except error_perm: # 认证错误
        print("ERROR: user Authentication failed ")
        AuthError = "ERROR: user Authentication failed "
        sys.exit(AuthError)
    return ftp

def UploadFile(ftp, localpath):
    """
    上传文件
    :param ftp:
    :param SentencesFile:
    :param localpath:
    :return:
    """
    bufsize = 1024 # 缓冲区大小
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + SentencesFile, fp, bufsize)  # 上传文件
    fp.close()

try:
    version = "v1.3.1"
    LatestVersion = requests.get("https://qn.nya-wsl.cn/scu/version.html").text

    if version != LatestVersion:
        UpdateInfo()
        UpdateUrl = "https://qn.nya-wsl.cn/scu/scu_update.exe"
        print("检测到更新，正在更新中...")
        request.urlretrieve(UpdateUrl,"scu_update.exe")
        os.system("scu_update.exe")
        sys.exit("exit code: update") # 防止更新程序异常导致程序继续运行

    TestInfo()
    tmp = open("tmp.ico","wb+")
    tmp.write(base64.b64decode(img))
    tmp.close()
    window = Tk()
    window.iconbitmap("tmp.ico")
    os.remove("tmp.ico")
    window.title(f"Nya-WSL | 语录上传系统{version}")
    window.geometry('400x300')

    LabelSentenceJsonName = Label(window, text="语录名称(桑吉、羽月、楠桐)")
    LabelSentenceText = Label(window, text="需要添加的语录")
    LabelSentenceAuthor = Label(window, text="谁说的(楠桐语录)")
    SentenceJsonName = Entry(window, width=5)
    SentenceText = Entry(window, width=30)
    SentenceAuthor = Entry(window, width=10)

    LabelSentenceJsonName.pack()
    SentenceJsonName.pack()
    LabelSentenceAuthor.pack()
    SentenceAuthor.pack()
    LabelSentenceText.pack()
    SentenceText.pack()

    btn = Button(window,fg="black",bg="white",text="上传语录",command=UploadSentence)
    btn.pack(pady=10)
    window.mainloop()
except:
    Mylogpetion()