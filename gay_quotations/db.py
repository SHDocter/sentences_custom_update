'''
Author: Nya-WSL
Copyright © 2023 by Nya-WSL All Rights Reserved. 
Date: 2023-11-01 12:30:35
LastEditors: 狐日泽
LastEditTime: 2023-12-28 16:32:05
'''
import sqlite3
from configs.path_config import DATA_PATH

ScuDataPath = DATA_PATH / "scu"
DatabasePath = ScuDataPath / "gay_quotations.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def create():
    conn = sqlite3.connect(DatabasePath)
    c = conn.cursor()
    c.execute("CREATE TABLE hitokoto(user NOT NULL,N INT,R INT,SR INT,SSR INT,upload_count INT,group_id)")
    conn.commit()
    conn.close()

def check(user):
    conn = sqlite3.connect(DatabasePath)
    c = conn.cursor()
    # 获取user表中所有的记录
    c.execute(f"SELECT * FROM hitokoto WHERE user = {user}")
    #获取结果
    result = c.fetchall()
    #关闭连接
    conn.close()
    return result

def write(user, group_id, n=0, r=0, sr=0, ssr=0, upload_count=0):
    conn = sqlite3.connect(DatabasePath)
    c = conn.cursor()
    c.execute("INSERT INTO hitokoto (user,N,R,SR,SSR,upload_count,group_id) VALUES (?,?,?,?,?,?,?)", (user, n, r, sr, ssr, upload_count, group_id))
    conn.commit()
    conn.close()

def uptate(user, CountDict):
    conn = sqlite3.connect(DatabasePath)
    for key,value in CountDict.items():
        c = conn.cursor()
        c.execute(f"UPDATE hitokoto SET {key}={key} + ? WHERE user = ?", (value, user))
        conn.commit()
    conn.close()

def count(user):
    conn = sqlite3.connect(DatabasePath)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(f"SELECT * FROM hitokoto WHERE user = {user}")
    DatabaseCount = c.fetchall()
    conn.close()
    return DatabaseCount

def sum():
    conn = sqlite3.connect(DatabasePath)
    c = conn.cursor()
    result = c.execute(f"SELECT SUM(upload_count) FROM hitokoto").fetchone()[0]
    conn.close()
    return result