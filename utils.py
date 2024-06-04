from typing import List, Tuple, Dict
import os
if False:
    from openai import OpenAI as LLM
else:
    from zhipuai import ZhipuAI as LLM
import time
import tiktoken

def usage():
    help_message = """Usage: -i/--initdb: update database
-h/--help: show usage
"""
    print(help_message)

def analyse_opt(opt: List[Tuple]):
    if len(opt[0]) == 0:
        return
    ret = {}
    for o, a in opt:
        if o in ('-x', '--help'):
            usage()
        if o in ('-i', '--initdb'):
            os.system("flask db migrate")
            os.system("flask db upgrade")
        elif o in ('-h', "--host"):
            ret["host"] = a
        elif o in ('-p', "--port"):
            ret["port"] = a
    return ret
            
def estimate_token_num(text: str, modelname: str) -> int:
    try:
        encoding = tiktoken.get_encoding(modelname)
    except ValueError as e:
        if modelname == "babbage-002":
            encoding = tiktoken.get_encoding("cl100k_base")
        else:
            print(e)
            print(f"Invalid model name: {modelname}")
            return 0
    return len(encoding.encode(text))

# 预估训练需要的token数目
def estimate_token_num_with_path(path: str, modelname: str) -> int:
    with open(path, 'r') as file:
        text = file.read()
    return estimate_token_num(text, modelname)

def temp_sleep(st = 0):
    if st > 0:
        time.sleep(st)
    else:
        time.sleep(1)

