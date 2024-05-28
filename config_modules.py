from typing import Optional
from flask import Flask
import json
import logging
from logging import config as logging_config
from extensions.Database import PostgresqlDatabase, RedisDatabase
from extensions.ext import db
from extensions.LLMClient import LLMClient
from extensions.MailService import MailService

if False:
    from openai import OpenAI as LLM
else:
    from zhipuai import ZhipuAI as LLM

def config_postgresql_database(app: Flask, filename: str = "config.json") -> Optional[PostgresqlDatabase]:
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["postgresql"]
            # dburl = f"{config_data['service']}://{config_data['username']}:{config_data['password']}@{config_data['hostname']}:{config_data['port']}/{config_data['databaseName']}"
            # app.config['SQLALCHEMY_DATABASE_URI'] = dburl
            # db.init_app(app)
            return PostgresqlDatabase(config=config_data)
    except FileNotFoundError:
        logging.getLogger("StreamLogger").error("Config file not found!")
        return None
    except KeyError:
        logging.getLogger("StreamLogger").error("Postgresql config file is missing keys!")
        return None

def config_logger(filename: str = "config.json"):
    config_data = None
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["logger"]
    except FileNotFoundError:
        print("Logger Config file not found!")
    if config_data:
        logging_config.dictConfig(config_data)
        # curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # logging.basicConfig(filename="log/" + curdate + " logging.log")
        FileLogger = logging.getLogger("FileLogger")
        FileLogger.info("Logging Configuration Loaded.")

def config_redis_database(filename: str = "config.json") -> Optional[RedisDatabase]:
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["redis"]
            return RedisDatabase(config_data)
    except FileNotFoundError:
        logging.getLogger("StreamLogger").error("Logger Config file not found!")
    except KeyError:
        logging.getLogger("StreamLogger").error("Redis config file is missing keys!")
        return None

def config_session(app : Flask, filename: str = "config.json"):
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["session"]
            app.config["SECRET_KEY"] = config_data["secret_key"]
            logging.getLogger("StreamLogger").info("Session initialied.")
            logging.getLogger("FileLogger").info("Session initialied.")

    except FileNotFoundError:
        logging.getLogger("StreamLogger").error("Session Config file not found!")
    except KeyError:
        logging.getLogger("StreamLogger").error("Session config file is missing keys!")

def config_openai_client(model_name: str = "gpt-3.5-turbo", filename: str = "config.json"):
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["LLM"]
            _client = LLM(api_key=config_data["api_key"])
            client = LLMClient(_client, model_name=model_name)
            return client
    except FileNotFoundError:
        logging.getLogger("StreamLogger").error("LLM Config file not found!")
    except KeyError:
        logging.getLogger("StreamLogger").error("LLM config file is missing keys!")

def config_mail(app: Flask, filename: str = "config.json"):
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)["mail"]
            app.config.update(
                MAIL_SERVER = config_data['mail_server'],
                MAIL_PORT = config_data["mail_port"],
                MAIL_USE_SSL = config_data["mail_use_ssl"],
                MAIL_USE_TSL = config_data["mail_use_tls"],
                MAIL_USERNAME = config_data['mail_username'],
                MAIL_PASSWORD = config_data['mail_password'],
                MAIL_DEFAULT_SENDER = (config_data["mail_default_sender"], config_data['mail_username']),
            )
            return MailService(app)
    except FileNotFoundError:
        logging.getLogger("StreamLogger").error("Mail Config file not found!")
    except KeyError:
        logging.getLogger("StreamLogger").error("Mail config file is missing keys!")
    