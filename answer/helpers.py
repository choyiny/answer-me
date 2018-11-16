from flask import session
from functools import wraps


# A collection of helper functions to help interact with Flask
from answer.models import Player


def gen_response(my_dict: dict):
    """
    Helper function to generate a response object that allows CORS.
    """
    from flask import jsonify
    response = jsonify(my_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def require_admin(func):
    """ require the session to be admin """
    from flask import session

    @wraps(func)
    def check_token(*args, **kwargs):
        # obtain the user
        player = get_current_player(session.get('username'))
        if player.is_admin:
            # proceed with original function
            return func(*args, **kwargs)
        else:
            # redirect with login
            return gen_response({"success": "False"})
    return check_token


def get_current_player(username):
    return Player.query.filter_by(player_name=username).first()
