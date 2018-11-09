from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

from answer import config
from answer.extensions import db
from answer.helpers import gen_response
from answer.security import require_admin_key
from answer.models import Player
from answer.game import Game

# initialize app with config params
app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)
socketio.on_namespace(Game('/game'))

# initialize connection to db
with app.app_context():
    # initialize connection to db
    db.init_app(app)

    # # Create all required models for database
    # from answer.models.player import Player
    db.create_all()


@app.route("/")
def index():
    """ Server index """
    return render_template("index.html")


@app.route("/tv")
def tv():
    """ TV index """
    return render_template("tv.html")


@app.route("/admin/register")
@require_admin_key
def register_players():
    """
    Registers the players to the database based on (SOME) as follows:

    [to be filled in]
    """
    # TODO: complete this function
    # example code to populate players
    emails = ['choyin.yong@mail.utoronto.ca', 'choyiny@gmail.com']

    for email in emails:
        player = Player(player_email=email)
        # add player to database queue
        db.session.add(player)
    # commit everything to the database
    db.session.commit()
