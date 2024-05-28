import sys
sys.path.append(sys.path[0] + "/..")
from ext import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)


class Preferences(db.Model):
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    style = db.Column(db.String(256), nullable=False)