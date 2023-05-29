import uuid
import json
import socket
from ftplib import FTP
from urllib import request
from ftplib import error_perm

from concurrent.futures import ThreadPoolExecutor


version = "1.2.0"
LatestVersion = "1.2.0"
print(f"当前版本：{version} 最新版本：{LatestVersion}")

def Choose():
    global choose
    global author
    global SentencesFile
    url = "http://sentence.osttsstudio.ltd:9000/" # 语录的获取url，需自行修改web服务器配置，需保留末尾的“/”
    JsonUrl = "" # 留空
    choose = input("""
1.桑吉
2.羽月
3.楠桐
请选择您所需要添加的语录并输入序号后按回车确认：
""")

    SentencesFile = ""
    if choose == "1":
        JsonUrl = url + "a.json" # 语录的获取url
        request.urlretrieve(JsonUrl,"a_local.json") # 下载语录到根目录
        SentencesFile = "a.json" # 更新后的语录文件名，建议与服务器上的文件名字保持一致
    elif choose == "2":
        JsonUrl = url + "b.json"
        request.urlretrieve(JsonUrl,"b_local.json")
        SentencesFile = "b.json"
    elif choose == "3":
        author = input("谁说的：") # 获取作者
        JsonUrl = url + "c.json"
        request.urlretrieve(JsonUrl,"c_local.json")
        SentencesFile = "c.json"
    else:
        input("该语录不存在，请检查！")
        Choose() # 返回选择

def InputSentences():
    sentence = input("""请输入需要添加的语录内容并按回车确认：
""")
    item_dict = "" # 留空
    OpenJsonFile = "" # 留空
    if choose == "1":
        OpenJsonFile = "a_local.json" # 与上方request的文件名一致
    if choose == "2":
        OpenJsonFile = "b_local.json"
    if choose == "3":
        OpenJsonFile = "c_local.json"
    f = open(OpenJsonFile, 'r', encoding="utf-8") # 将语言文件写入缓存
    text = f.read() # 读取语言
    f.close() # 关闭语言文件
    content = json.loads(text) # 转为List，List中为字典
    id = len(content) + 1 # 获取字典位数并加1的方式自动更新id
    Uuid = str(uuid.uuid4()) # 基于随机数生成uuid，可能会有极小的概率重复
    if choose == "1":
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
    elif choose == "2":
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
    elif choose == "3":
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

# 连接远程服务器
host = '' # 脱敏
port = 21
username = '' # 脱敏
password = '' # 脱敏

def ftpconnect(host, port, username, password):
    ftp = FTP()
    ftp.set_debuglevel(2) # 打开调试级别2，显示详细信息
    ftp.encoding = 'utf-8' # 解决中文编码问题，默认是latin-1
    try:
        ftp.connect(host, port)
        ftp.login(username, password)
        print(ftp.getwelcome()) # 打印欢迎信息
    except(socket.error, socket.gaierror): # 连接错误
        print("ERROR: cannot connect [{}:{}]" .format(host, port))
        return None
    except error_perm: # 认证错误
        print("ERROR: user Authentication failed ")
        return None
    return ftp

def uploadfile(ftp, localpath):
    """
    上传文件
    :param ftp:
    :param SentencesFile:
    :param localpath:
    :return:
    """
    bufsize = 1024 # 缓冲区大小
    print("FTP当前路径:", ftp.pwd())
    fp = open(localpath, 'rb')
    res = ftp.storbinary('STOR ' + SentencesFile, fp, bufsize)  # 上传文件
    if res.find('226') != -1:
        print('upload file complete', SentencesFile)
        print("文件列表:", ftp.nlst())
    fp.close()

Choose()
InputSentences()

ftp = ftpconnect(host, port, username, password)
file_list = ftp.nlst()
print(file_list)
# 避免提示 ftplib.error_perm: 550 SIZE not allowed in ASCII
ftp.voidcmd('TYPE I')
uploadfile(ftp, SentencesFile) # 上传文件
ftp.close()
