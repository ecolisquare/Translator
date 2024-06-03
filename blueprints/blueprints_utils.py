import random
from typing import Optional, Dict

def generate_random_str(length: int, limit='1234567890abcdefghijklmnopqrstuvwxyz') -> str:
    ret = ""
    for _ in range(length):
        ret += random.choice(limit)

def save_captcha_to_redis():
    pass

def wrap_ret_status(statusCode: int, message: Optional[str] = None):
    return {
        "statusCode": statusCode,
        "message": message
    }

def wrap_ret_json(retStaus: Dict, data: Optional[Dict] = None):
    return {
        "data": data,
        "status": retStaus
    }

def wrap_llm_response(data: dict):
    ret = {
        "id": f"chatcmpl-{generate_random_str(29)}",
        "object": "chat.completion",
        "created": 1717117211,
        "model": "gpt-3.5-turbo-0125",
        "choices": [
            {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": data["text"]
            },
            "logprobs": None,
            "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": data["prompt_tokens"],
            "completion_tokens": data["completion_tokens"],
            "total_tokens": data["total_tokens"]
        },
        "system_fingerprint": None
    }
    return ret