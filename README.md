# 后端代码
## 环境要求
### 数据库
本项目使用的数据库是Postgresql。本来打算用SQLAlchemy的，但是问题太多，那些莫名其妙的bug不知道怎么修，所以数据库都是用psycopg2+原生SQL完成的。如果你想使用其他的数据库，就得稍微改改代码。
所以首先你需要根据官方教程安装Postgresql数据库。正常安装后，Postgresql的默认服务端口是5432，这也是本项目使用的端口。想改就去config.json里改。
### Python环境
Python 3.10.13。且在conda环境中。至于包，请看：
```bash
pip install -r requirements.txt
```
## 运行
```bash
python app.py
```
预期结果：
```bash
2024-05-29 01:04:03,109 - [Database.py:22] - INFO - Postgresql Database initialized.
2024-05-29 01:04:03,126 - [LLMClient.py:24] - INFO - LLMClient initialied.
2024-05-29 01:04:03,126 - [config_modules.py:61] - INFO - Session initialied.
2024-05-29 01:04:03,126 - [Database.py:136] - INFO - Redis Database initialied.
2024-05-29 01:04:03,127 - [MailService.py:10] - INFO - Mail Service initialied.
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
...
```
服务默认在本地5000端口开启。