from flask import Flask, request, render_template, session
from flask_socketio import SocketIO
import csv
import queue

from sqlalchemy.exc import IntegrityError

from answer import config
from answer.extensions import db
from answer.helpers import gen_response, require_admin, get_current_player, get_player_by_nickname
from answer.models import Player, Question, QuickQuestion
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
    if request.form.get('nickname') is None:
        return gen_response({'success': True, 'message': 'please input nickname'})
    if request.form.get('username') is not None:
        username = request.form.get('username').lower().strip()
        nickname = request.form.get('nickname').lower().strip()
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

            return gen_response({'success': True, 'username': username, 'nickname': nickname})
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
    Registers the players to the database based on the uploaded files.
    
    Format of file uploaded: a list of email addresses separated by newline character.
    """
    # the file handle for the file csv
    file_handle = request.files['file']

    for line in file_handle:
        player = Player(player_name=line.split("@")[0].lower())
        db.session.add(player)
    db.session.commit()

    return gen_response({'success': 'True'})


@app.route("/admin/import_questions", methods=["POST"])
@require_admin
def import_questions():
    """
    Imports the questions.
    
    File format: A CSV with the following format
    question, correct answer, wrong answer 1, wrong answer 2, wrong answer3, wrong answer 4
    """
    # reset everything
    Question.query.delete()
    db.session.commit()

    file_handle = request.files['file']

    if not file_handle:
        return gen_response({'success': False})

    csv_reader = csv.reader([line.decode("utf-8") for line in file_handle.readlines()])

    for question, correct, wrong1, wrong2, wrong3, wrong4 in csv_reader:
        question_obj = Question(question=question, correct=correct, wrong1=wrong1,
                                wrong2=wrong2, wrong3=wrong3, wrong4=wrong4)
        db.session.add(question_obj)
    db.session.commit()

    return gen_response({'success': True})


@app.route("/admin/import_quick_questions", methods=["POST"])
@require_admin
def import_quick_questions():
    """
    Imports the quick questions
    
    File format: A list of question separated by new line character.
    """
    # reset everything
    QuickQuestion.query.delete()
    db.session.commit()

    # the file handle for the file csv
    file_handle = request.files['file']

    for line in file_handle:
        q = QuickQuestion(question=line.decode('utf-8').strip())
        db.session.add(q)
    db.session.commit()

    return gen_response({'success': 'True'})


@app.route("/admin/next_question", methods=['POST'])
@require_admin
def next_question():
    """
    Selects the next question in the database and broadcast it to all
    
    TODO: Rewrite so that admins broadcast it through socket. 
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
    """
    Logout all connected players
    
    TODO: Rewrite so that admins broadcast it through socket. 
    """
    game.emit("logout_everyone")
    return gen_response({'success': True})


@app.route("/admin/bump_to_lobby", methods=['POST'])
@require_admin
def back_to_lobby():
    """
    Move all connected players back to lobby
    
    TODO: Rewrite so that admins broadcast it through socket. 
    """
    if quick_answer_queue.qsize() > 0:
        previous = quick_answer_queue.get()
        game.add_score(get_player_by_nickname(previous), 500)
        quick_answer_queue.queue.clear()
    players = Player.query.order_by(Player.score).all()
    d = []
    for p in players:
        d.append([p.get_name(), p.score])
    game.emit("lobby", d[::-1])
    if game.correct_answer_text:
        game.emit("correct_answer", game.correct_answer_text)
    return gen_response({'success': True})


@app.route("/admin/next_quick_question", methods=['POST'])
@require_admin
def next_quick_question():
    """
    Select the next quick question and broadcast
    
    TODO: Rewrite so that admins broadcast it through socket. 
    """
    game.reset()

    question: QuickQuestion = QuickQuestion.query.filter_by(asked=False).order_by(QuickQuestion.question_id).first()

    game.emit("quick", question.question)

    question.asked = True
    db.session.add(question)
    db.session.commit()

    return gen_response({'success': True})


@socketio.on("first_click", namespace="/game")
def first_guy_click(data):
    """
    For a connected player, queue up to answer a quick question.
    
    """
    if quick_answer_queue.qsize() == 0:
        game.emit("first_guy", data)
    quick_answer_queue.put(data)
    print(data, "clicked")
    return gen_response({'success': True})


@app.route("/admin/next_player", methods=['POST'])
@require_admin
def next_player():
    """
    Selects the next player in queue to answer quick questions
    
    """
    previous = quick_answer_queue.get()
    player = get_player_by_nickname(previous)
    game.add_score(player, -(int(player.score * 0.05)))
    if quick_answer_queue.qsize() > 0:
        game.emit("first_guy", quick_answer_queue.queue[0])
    return gen_response({'success': True})
