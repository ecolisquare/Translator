import psycopg2
from typing import Optional, Dict
from flask import Flask
import logging
from flask_sqlalchemy import SQLAlchemy
import redis
import sys , os
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
from DatabaseModels.operations import *

user_table_name = "users"
user_preference_table_name = "preferences"

class PostgresqlDatabase:
    conn = None
    def __init__(self, config):
        self.__config_list__ = config
        self.connect()
        PostgresqlDatabase.__instance = self
        streamLogger = logging.getLogger("StreamLogger")
        streamLogger.info("Postgresql Database initialized.")
    
    def connect(self):
        logger = logging.getLogger("FileLogger")
        streamLogger = logging.getLogger("StreamLogger")
        try:
        # connecting to the PostgreSQL server
            with psycopg2.connect(host=self.__config_list__["hostname"],
                                   dbname=self.__config_list__["databaseName"],
                                     user=self.__config_list__["username"], 
                                     password=self.__config_list__["password"]) as conn:
                cursor = conn.cursor()
                logger.info("PostgreSQL server information:")
                # Executing a SQL query
                cursor.execute("SELECT version();")
                # Fetch result
                record = cursor.fetchone()
                logger.info(f"You are connected to - {record}")
                logger.info(f'Connected to the PostgreSQL server at {self.__config_list__["hostname"]}:{self.__config_list__["port"]}.')
                self.conn = conn
        except Exception as error:
            streamLogger.error(f'Error while connecting to the PostgreSQL server: {error}')
            logger.error(error)
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
    
    # return code if fetchResult = false, else return tuple
    def _excute(self, query: str, values: Optional[tuple], fetchResult=False):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, values)
                self.conn.commit()
                if fetchResult:
                    return cur.fetchall()
                else:
                    return 0
        except Exception as error:
            logger = logging.getLogger("FileLogger")
            logger.error(error)
            logger.error(f"Error on excuting sql {query}")
            return []
    
    # return  -1 if failed.
    def insert_item(self, tableName: str ,item: dict) -> int:
        columns = ','.join(item.keys())
        values = list(item.values())
        for i in range(len(values)):
            if type(values[i]) == list:
                values[i] = self._generate_array(values[i])
            else:
                values[i] = "'" + values[i] + "'"
        values = ','.join(values)
        sql = """INSERT INTO {tableName}({columns}) VALUES({values});""".format(tableName=tableName, columns=columns, values=values)
        return self._excute(sql, values)

    # return new item dict if succeeded, None if failed.
    # To do: consider array
    def get_item(self, tableName: str, pkeyname, pkeyvalue, conditions: dict = None):
        if pkeyvalue is not None:
            pkeyvalue = "'" + pkeyvalue + "'"
            if conditions is not None:
                sql = """SELECT * FROM {tableName} WHERE {pkeyname}={pkeyvalue}""".format(tableName=tableName, pkeyname=pkeyname, pkeyvalue=pkeyvalue, conditions=conditions)
                for key, value in conditions.items():
                    condition = " AND '" + key + "'='" + value + "'"
                    sql += condition
                sql += ";"
            else:
                sql = """SELECT * FROM {tableName} WHERE {keyname}={keyvalue};""".format(tableName=tableName, keyname=pkeyname, keyvalue=pkeyvalue)
            res = self._excute(sql, (pkeyvalue,), fetchResult=True)
            return res[0] if len(res) > 0 else None

    # return True if succeeded, False if failed.
    def update_item(self, tableName: str, pkeyname, pkeyvalue, item: dict) -> bool:
        for key in item.keys():
            item[key] = "'" + item[key] + "'"
        pkeyvalue = "'" + pkeyvalue + "'"
        setVals = ','.join([f"{key}={value}" for key, value in item.items()])
        sql = """UPDATE {tableName} set {setVals} WHERE {pkeyname}={pkeyvalue};""".format(tableName=tableName, setVals=setVals, pkeyname=pkeyname, pkeyvalue=pkeyvalue)
        return self._excute(sql, tuple([*item.values(), pkeyvalue]))
    
    def _generate_array(self, array: list) -> str:
        ret = "'{"
        for i in range(len(array) - 1):
            ret += '"' + array[i] + '",'

        ret += '"' + array[-1] + '"}'
        ret += "'"
        return ret
    # def insert_item(self, tableName: str, item: dict) -> Optional[int]:
    #     id = -1
    #     if tableName == user_table_name :
    #         id = user_info_create_user(item["username"], item["password"], item["email"])
    #         # 也应同时创建preferences表中的字段
    #         preferences_create_user(id)
    #     return id
    
    # def get_item(self, tableName: str, itemId: Optional[int] = None, email: Optional[str] = None) -> Optional[dict]:
    #     if tableName == user_table_name:
    #         return user_info_get_user(itemId, email)
    #     if tableName == user_preference_table_name:
    #         return preferences_get_user(itemId)
    #     return None
    
    # def update_item(self, tableName: str, itemId: int, item: dict) -> bool:
    #     if tableName == user_table_name:
    #         return user_info_update_user(itemId, item["username"], item["password"], item["email"])
    #     elif tableName == user_preference_table_name:
    #         return preferences_update_style(itemId, item["style"])
 
    # def delete_item(self, tableName: str, itemId: int):
    #     if tableName == user_table_name:
    #         preferences_delete_user(itemId)
    #         return user_info_delete_user(itemId)
        
    @staticmethod
    def get_instance():
        if PostgresqlDatabase.__instance:
            return PostgresqlDatabase.__instance
        else:
            raise Exception("PostgresqlDatabase instance not initialized")


class RedisDatabase:
    __pool = None
    def __init__(self, config) -> None:
        self.__pool = redis.ConnectionPool(host=config['host'], port=config['port'])
        self.__expire_time = config['expire_time']
        RedisDatabase.__instance = self
        streamLogger = logging.getLogger("StreamLogger")
        streamLogger.info("Redis Database initialied.")

    def save_item(self, key, value) -> bool:
        r = redis.Redis(connection_pool=self.__pool)
        r.set(key, value, px=self.__expire_time)

    def get_item(self, key):
        r = redis.Redis(connection_pool=self.__pool)
        return r.get(key)

    @staticmethod
    def get_instance():
        if RedisDatabase.__instance:
            return RedisDatabase.__instance
        else:
            raise Exception("RedisDatabase instance not initialized")


