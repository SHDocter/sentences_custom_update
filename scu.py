import os
import uuid
import json

version = "1.1.0"
LatestVersion = "1.1.0"
print(f"当前版本：{version} 最新版本：{LatestVersion}")

def Choose():
    global path
    global choose
    global author
    global SentencesFile
    path = "/root/sentences/sentences/" # 语录的路径
    JsonPath = "" # 留空
    choose = input("""
1.桑吉
2.羽月
3.楠桐
请选择您所需要添加的语录并输入序号后按回车确认：
""")

    SentencesFile = ""
    if choose == "1":
        JsonPath = path + "a.json" # 语录文件
        os.system(f"cp -r {JsonPath} {path}/scu")
        SentencesFile = "a.json" # 更新后的语录文件名
    elif choose == "2":
        JsonPath = path + "b.json"
        os.system(f"cp -r {JsonPath} {path}/scu")
        SentencesFile = "b.json"
    elif choose == "3":
        author = input("谁说的：") # 获取作者
        JsonPath = path + "c.json"
        os.system(f"cp -r {JsonPath} {path}/scu")
        SentencesFile = "c.json"
    else:
        input("该语录不存在，请检查！")
        Choose() # 返回选择

def InputSentences():
    sentence = input("""请输入需要添加的语录内容并按回车确认：
""")
    item_dict = "" # 留空
    os.system(f"mkdir {path}/scu")
    f = open(f"{path}/scu/{SentencesFile}", 'r', encoding="utf-8") # 将语言文件写入缓存
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
    "type": "a",
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
    "type": "a",
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

    with open(f"{path}/scu/{SentencesFile}", 'w', encoding="utf-8") as JsonFile:
        json.dump(content, JsonFile, indent=4, ensure_ascii=False) # 打开并写入json中，保持4格缩进并避免中文乱码
    os.system(f"cp -r {path}/scu/{SentencesFile} {path}")
    os.system("/root/hitokoto-api/restart.sh")

Choose()
InputSentences()