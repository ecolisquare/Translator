import random
from typing import Optional, Dict

def generate_random_number_str(bit: int) -> str:
    ret = ""
    for _ in range(bit):
        ret += str(random.randint(0, 9))
    return ret

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