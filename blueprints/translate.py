from flask import Blueprint
from flask import request, session, g
from flask_mail import Message
from extensions.MailService import MailService
from .blueprints_utils import generate_random_number_str, wrap_ret_json, wrap_ret_status
import logging
import json
import sys
cwd = sys.path[0]
cwd += "/.."
sys.path.append(cwd)
from extensions.Database import PostgresqlDatabase
from extensions.LLMClient import LLMClient
from constexpr import SUCCESS, ERROR

bp = Blueprint('translate', __name__, url_prefix='/translate')

@bp.route('/', methods=['POST'])
def translate():
    client = LLMClient.get_instance()
    params = json.loads(request.get_data())
    db = PostgresqlDatabase.get_instance()
    username = session["username"]
    style = db.get_item("preferences", pkeyname='username', pkeyvalue=username)[1]
    ans = client.translate(params['text'], params['source_language'], params['target_language'], style=style)
    if params['text'] != "" and ans == "":
        status = wrap_ret_status(ERROR, "LLM API error. Failed to translate.")
    else:
        status = wrap_ret_status(SUCCESS)
    data = {
        "translation": ans
    }
    return wrap_ret_json(status, data)

@bp.route('/modifications', methods=['POST'])
def store_modifications():
    client = LLMClient.get_instance()
    params = json.loads(request.get_data())
    style = client.infer_translation_style(params["modifications"])
    if style == "":
        status = wrap_ret_status(ERROR, "LLM API error. Failed to infer translation styles.")
    else:
        status = wrap_ret_status(SUCCESS)
        # 存储风格
        db = PostgresqlDatabase.get_instance()
        username = session["username"]
        db.update_item("preferences", pkeyname='username', pkeyvalue=username, item={"style": style})
    return wrap_ret_json(status)