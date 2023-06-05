# Sentences Custom Update

![python](https://img.shields.io/badge/Version-1.4.0-cyan) ![python](https://img.shields.io/badge/Python-3.11.3-blue) ![os](https://img.shields.io/badge/OS-remote|Windows-orange) ![os](https://img.shields.io/badge/OS-local|All-orange)

bot插件扩展，用于快速更新语录库

## 如何使用

#### scu_local

- 安装并运行pm2

```
cd /root/hitokoto-api
npm i -g pm2
pm2 startup
pm2 start ecosystem.config.js --env production
pm2 save
```

- 运行程序

`python3 scu_local.py`

#### scu_remote

- Windows

`scu_remote.exe`

- Linux

`python3 scu_remote.py # 因为scu_remote是为Windows设计的，不推荐在Linux中使用>= 1.2.1版本的scu_remote`
