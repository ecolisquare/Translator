from flask import Blueprint
from flask import request, session, g
from flask_mail import Message
from extensions.MailService import MailService
from .blueprints_utils import wrap_ret_json, wrap_ret_status, generate_random_str
import logging
import json
import sys
cwd = sys.path[0]
cwd += "/.."
sys.path.append(cwd)
from extensions.Database import RedisDatabase, PostgresqlDatabase
from .crypto import encrypt_password, verify_password
from constexpr import SUCCESS, ERROR

# /auth
bp = Blueprint("auth", __name__, url_prefix="/auth")
user_table_name = "user_info"

@bp.route("/login", methods=["POST"])
def login():
    send_data = json.loads(request.get_data())
    username = send_data["username"]
    userinfo = PostgresqlDatabase.get_instance().get_item(user_table_name, 'username', username)
    status = {}
    if userinfo is None:
        status = wrap_ret_status(ERROR, "Unregistered username")
    elif not verify_password(send_data["password"], userinfo[1]):
        status = wrap_ret_status(ERROR, "Wrong password")
    else:
        status = wrap_ret_status(SUCCESS, "Login success")
        session['username'] = username
    return wrap_ret_json(status)
    

@bp.route("/register", methods=["POST"])
def register():
    send_data = json.loads(request.get_data())
    send_data["password"] = encrypt_password(send_data["password"])
    code = PostgresqlDatabase.get_instance().insert_item(user_table_name, send_data)
    if code < 0:
        return json.dumps(wrap_ret_json(wrap_ret_status(ERROR, "Register failed. Username already exists.")))
    return json.dumps(wrap_ret_json(wrap_ret_status(SUCCESS)))
    

@bp.route("/email_captcha", methods=["POST"])
def send_captcha():
    email = json.loads(request.get_data())["email"]
    captcha = generate_random_str(6, '1234567890')
    mailService = MailService.get_instance()
    mailService.send_mail(subject="Verify your account", recipients=[email], body=f"Your verification code is {captcha}")
    fileLogger = logging.getLogger("FileLogger")
    fileLogger.info(f"Sent captcha {captcha} to {email}")

    # redisdb = RedisDatabase.get_instance()
    # redisdb.save_item(email, captcha)

    status = wrap_ret_status(SUCCESS, "Captcha sent.")
    return wrap_ret_json(status, {"captcha": captcha})

@bp.route("/update", methods=["POST"])
def update_userinfo():
    # post the whole form
    send_data = json.loads(request.get_data())
    username = send_data['username']
    send_data.pop('username')
    if PostgresqlDatabase.get_instance().update_item(user_table_name, pkeyname='username', pkeyvalue=username, item=send_data) == 0:
        return json.dumps(wrap_ret_json(wrap_ret_status(SUCCESS)))
    else:
        return json.dumps(wrap_ret_json(wrap_ret_status(ERROR, "Update failed")))

