from db import register_player, login_player


def register(username, password, confirm_password):

    username = username.strip()

    if username == "":
        return False, "Username cannot be empty."

    if password == "":
        return False, "Password cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    return register_player(username, password)


def login(username, password):

    username = username.strip()

    if username == "":
        return None, "Enter your username."

    if password == "":
        return None, "Enter your password."

    return login_player(username, password)