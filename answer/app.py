from flask import Flask, request, render_template, session
from flask_socketio import SocketIO
import random
import time
import csv
import queue

from sqlalchemy.exc import IntegrityError

from answer import config
from answer.extensions import db
from answer.helpers import gen_response, require_admin, get_current_player
from answer.models import Player, Question
from answer.game import Game

# initialize app with config params
app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)
game = Game('/game')
socketio.on_namespace(game)
quick_answer_queue = queue.Queue()


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
    # regular user
    if request.form.get('username') is not None:
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        player = get_current_player(username)

        # player can be found
        if player is not None:
            # update nickname
            if nickname is not None and len(nickname) > 0:
                player.nickname = nickname
                db.session.add(player)
                try:
                    db.session.commit()
                except IntegrityError:
                    return gen_response({'success': False, 'message': 'nickname not unique'})

            # set user session
            session['username'] = username

            return gen_response({'success': True, 'username': username})
        else:
            # player cannot be found in database
            return gen_response({'success': False, 'message': 'must use registered email prefix'})


@app.route("/logout", methods=["POST"])
def logout():
    session['username'] = None
    return gen_response({'success': True})


@app.route("/lee/admin")
@require_admin
def admin():
    """ Admin control panel """
    return render_template("admin.html")


@app.route("/admin/register", methods=["POST"])
@require_admin
def register_players():
    """
    Registers the players to the database based on (SOME) as follows:

    [to be filled in]
    """
    # the file handle for the file csv
    file_handle = request.files['file']

    for line in file_handle:
        player = Player(player_name=line.split("@")[0])
        db.session.add(player)
    db.session.commit()

    return gen_response({'success': 'True'})


@app.route("/admin/import_questions", methods=["POST"])
@require_admin
def import_questions():
    """
    Imports the questions
    """
    # reset everything
    Question.query.delete()
    db.session.commit()

    file_handle = request.files['file']

    if not file_handle:
        return gen_response({'success': False})

    csv_reader = csv.reader([line.decode("utf-8") for line in file_handle.readlines()])

    for question, correct, wrong1, wrong2, wrong3 in csv_reader:
        question_obj = Question(question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)
        db.session.add(question_obj)
    db.session.commit()

    return gen_response({'success': True})


@app.route("/admin/next_question", methods=['POST'])
@require_admin
def next_question():
    """
    Selects the next question in the database and broadcast it to all
    """
    question: Question = Question.query.filter_by(asked=False).first()
    if question:
        question_dict = question.get_dict()
        # a multiple choice question has been emitted
        game.emit("multiple_choice", question_dict)

        # reset starting time and players who answered the question
        game.reset()

        # keep track of the question id in the game and the correct answer text to display on tv
        game.correct_answer_idx = question_dict['answers'].index(question.correct_answer) + 1
        game.correct_answer_text = question.correct_answer

        # the question is now asked and cannot be selected again
        question.asked = True
        db.session.add(question)
        db.session.commit()

        return gen_response({'success': True})


@app.route("/admin/reset", methods=['POST'])
@require_admin
def reset_everyone():
    game.emit("logout_everyone")
    return gen_response({'success': True})


@app.route("/admin/bump_to_lobby", methods=['POST'])
@require_admin
def back_to_lobby():
    players = Player.query.order_by(Player.score).all()
    d = []
    for p in players:
        d.append([p.get_name(), p.score])
    game.emit("lobby", d[::-1])
    return gen_response({'success': True})


@app.route("/admin/swicth_to_quick", methods=['POST'])
@require_admin
def switch_to_quick():
    game.emit("quick", "message")
    return gen_response({'success': True})


@app.route("/admin/next_quick_question", methods=['POST'])
@require_admin
def next_quick_question():
    quick_answer_queue.queue.clear()
    return gen_response({'success':True})


@socketio.on("first_click", namespace="/game")
def first_guy_click(data):
    if quick_answer_queue.qsize() == 0:
        game.emit("first_guy", data)
    quick_answer_queue.put(data)
    print("PUT:", data, "SIZE:", quick_answer_queue.qsize())
    return gen_response({'success': True})


@app.route("/admin/next_player", methods=['POST'])
@require_admin
def next_player():
    print("SIZE:", quick_answer_queue.qsize())
    if quick_answer_queue.qsize() > 0:
        game.emit("first_guy", quick_answer_queue.get())
    return gen_response({'success': True})
