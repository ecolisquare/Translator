import bcrypt


def encrypt_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, standard_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), standard_password.encode("utf-8"))