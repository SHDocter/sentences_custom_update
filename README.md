# Sentences Custom Update

![python](https://img.shields.io/badge/Version-1.4.1-cyan) ![python](https://img.shields.io/badge/Python-3.11.4-blue) ![os](https://img.shields.io/badge/OS-remote|Windows-orange) ![os](https://img.shields.io/badge/OS-local|All-orange)

bot插件扩展，用于快速更新语录库

## 如何使用

#### server

- 安装并运行pm2

```
cd /root/hitokoto-api
npm i -g pm2
pm2 startup
pm2 start restart.config.js # 出于安全考虑 redis需改为仅本地访问并添加密码 所以需要在服务器持久化进行刷新数据库的操作 同时上传的语录保存位置不能为语录库 该部分代码需自行编写 需要在配置文件中设置watch语录文件的变更并取消自动重启
pm2 start ecosystem.config.js --env production # 需要在配置文件中设置watch语录文件的变更
pm2 save
```

#### scu_local

- 运行程序

`python3 scu_local.py`

#### scu_remote

- Windows

`scu_remote.exe`

- Linux

```
# 未测试
# 目前版本无法使用，将在后续更新中考虑适配

pip install -r requirements.txt
python3 scu_remote_cmd.py # 因为scu_remote_gui是为Windows设计的，不推荐在Linux中使用scu_remote_gui，且无法在非desktop中运行
```

- Mac

```
# 未测试
# 目前版本无法使用，将在后续更新中考虑适配

pip install -r requirements.txt
python3 scu_remote_cmd.py # 因为scu_remote_gui是为Windows设计的，不推荐在Mac中使用scu_remote_gui
```

#### Web | 开发中

- Server

`...`

- Client

[Nya-WSL | 语录上传系统](http://upload-yulu.nya-wsl.cn)