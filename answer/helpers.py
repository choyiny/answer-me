from functools import wraps


# A collection of helper functions to help interact with Flask
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
    from flask import session, redirect

    @wraps(func)
    def check_token(*args, **kwargs):
        # obtain the user
        if session.get('username') == "novelty-admin!":
            # proceed with original function
            return func(*args, **kwargs)
        else:
            # redirect with login
            return redirect('/')
    return check_token
