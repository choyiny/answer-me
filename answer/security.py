from flask import request

from answer.models import Player

API_KEY = "noveltyforlife"


def require_player_email(func):
    """
    The view function requires a player email to exists in the json with the player's email.
    """
    def check_token(*args, **kwargs):
        # if the token is a valid API key
        if Player.query.filter_by(email=request.get_json().get('email')).first():
            # proceed with original function
            return func(*args, **kwargs)
        else:
            return {"success": False, "errors": ["You do not have permissions to view the resource."]}
    return check_token



def require_admin_key(func):
    """
    Decorator put on top of a resource function.

    Adapted from: https://stackoverflow.com/questions/32510290/how-do-you-implement-token-authentication-in-flask

    Requires an API token in the request header to access the view.
    :param func: A resource function that requires API authentication
    :return: A wrapper function to check the token
    """
    def check_token(*args, **kwargs):
        # if the token is a valid API key
        if request.headers.get("Authorization") == f"Bearer {API_KEY}":
            # proceed with original function
            return func(*args, **kwargs)
        else:
            return {"success": False, "errors": ["You do not have permissions to view the resource."]}
    return check_token
