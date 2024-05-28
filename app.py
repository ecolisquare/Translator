from flask import Flask, session, g, make_response
from flask_cors import CORS, cross_origin
import sys
from config_modules import config_postgresql_database, config_logger, config_redis_database, config_session, config_mail, config_openai_client, config_mail
from utils import *
from getopt import getopt, GetoptError
from blueprints.authorization import bp as auth_bp
from blueprints.translate import bp as translate_bp

app = Flask(__name__)
# http://10.219.187.164:5173
cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
app.register_blueprint(auth_bp)
app.register_blueprint(translate_bp)


# hooks
@app.before_request
def get_user_info():
    user_id = session.get("user_id")
    if user_id:
        user = db.get_item("user_info", user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)

@app.route('/')
@cross_origin()
def hello_world():
    return "Hello, World!"


@app.after_request
def after(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp

if __name__ == '__main__':
    config_logger()
    # db is PostgresqlDatabase object
    db = config_postgresql_database(app)
    client = config_openai_client()
    config_session(app)
    rdb = config_redis_database()
    mail = config_mail(app)

    try:
        ret = getopt(sys.argv[1:], "hi", ["help", "init"])
        analyse_opt(ret)
    except GetoptError:
        print("Error: unknown arguments")
        usage()
        sys.exit(1)
    app.run(debug=True)
    db.disconnect()

