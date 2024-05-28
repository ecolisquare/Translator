from .models import *
from typing import Optional

def preferences_update_style(user_id: int, style: str):
    user = Preferences.query.get(user_id)
    if user:
        user.style = style
        db.session.commit()
        return True
    return False

def preferences_delete_user(user_id: int):
    user = Preferences.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def preferences_create_user(userid: int, style=""):
    new_user = Preferences(id=userid, style=style)
    db.session.add(new_user)
    db.session.commit()
    return new_user.id

def preferences_get_user(user_id: int):
    return Preferences.query.get(user_id)

def user_info_update_user(user_id: int, username: Optional[str] = None, password: Optional[str] = None, email: Optional[str] = None):
    user = User.query.get(user_id)
    if user:
        if username is not None:
            user.username = username
        if password is not None:
            user.password = password
        if email is not None:
            user.email = email
        db.session.commit()
        return True
    return False

def user_info_delete_user(user_id: int):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def user_info_create_user(username: str, password: str, email: str):
    last_user_id = User.query.order_by(User.id.desc()).first()
    if last_user_id is None:
        user_id = 1
    else:
        user_id = last_user_id.id + 1
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return -1
    new_user = User(id=user_id, username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    return new_user.id

def user_info_get_user(user_id: Optional[int], email: Optional[str]):
    if user_id is not None:
        return User.query.get(user_id)
    elif email is not None:
        return User.query.filter_by(email=email).first()
    return None