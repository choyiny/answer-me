from flask import Flask, request, render_template, session
from flask_socketio import SocketIO
import random

from answer import config
from answer.extensions import db
from answer.helpers import gen_response, require_admin
from answer.models import Player, Question
from answer.game import Game

# initialize app with config params
app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)
game = Game('/game')
socketio.on_namespace(game)


# initialize connection to db
with app.app_context():
    # initialize connection to db
    db.init_app(app)


@app.route("/")
def index():
    """ Server index """
    return render_template("index.html")


@app.route("/tv")
def tv():
    """ TV index """
    return render_template("tv.html")


@app.route("/login", methods=['POST'])
def login():
    """ Login to obtain session cookie if available """
    # novelty admin
    if request.form.get('username') == 'novelty-admin!':
        session['username'] = 'novelty-admin!'
        return gen_response({'success': True, 'username': 'novelty-admin!'})
    # regular user
    if request.form.get('username') is not None:
        username = request.form.get('username')
        if Player.query.filter_by(player_name=username).first() is not None:
            session['username'] = username
            return gen_response({'success': True, 'username': username})
        else:
            return gen_response({'success': False})


@app.route("/logout")
def logout():
    session['username'] = None
    return gen_response({'success': True})


@app.route("/admin/register")
@require_admin
def register_players():
    """
    Registers the players to the database based on (SOME) as follows:

    [to be filled in]
    """
    # TODO: complete this function

    for name in ['choyin.yong', 'bowei.liu']:
        player = Player(player_name=name)
        # add player to database queue
        db.session.add(player)
    # commit everything to the database
    db.session.commit()


@app.route("/admin/import_questions")
@require_admin
def import_questions():
    """
    Imports the questions
    """
    # reset everything
    Question.query.delete()
    db.session.commit()

    questions_list = []

    # read some csv into list

    # shuffle order here
    random.shuffle(questions_list)

    # import into database for each
    for question_dict in questions_list:
        question_obj = Question(**question_dict)
        db.session.add(question_obj)
    db.session.commit()


@app.route("/admin/next_question")
@require_admin
def next_question():
    """
    Selects the next question in the database and broadcast it to all
    :return:
    """
    question = Question.query.filter_by(asked=False).first()

    game.emit("multiple_choice", question.get_dict())
    
    question.asked = True
    db.session.add(question)
    db.session.commmit()

    return gen_response({'success': True})


@app.route("/admin/reset")
@require_admin
def reset_everyone():
    game.emit("logout_everyone");
