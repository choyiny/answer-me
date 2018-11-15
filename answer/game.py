import time
from queue import Queue
from flask_socketio import Namespace
from flask import session

from answer.helpers import get_current_player
from answer.extensions import db


class Game(Namespace):
    """
    Queue the players according to who click the button the fastest.

    """
    # queue to keep track of who clicks the fastest in gamemode 2
    answer_queue = Queue()

    # correct answer's index
    correct_answer_text = None
    correct_answer_idx = -1

    # starting time of the question
    starting_time = -1

    # players who answered
    answered = set()

    def on_connect(self):
        """
        Authenticates the person trying to connect to the socket
        :return: False if authentication failure
        """
        if session.get('username') is None:
            return False
        if get_current_player(session.get('username')) is None:
            return False

    def on_answer_option(self, data):
        """ data is formatted as {"answer_number": 1} """
        if data['answer_number'] == self.correct_answer_idx:

            # time taken to answer the question = end time - start time
            time_taken = time.time() - self.starting_time

            print(f"{session['username']} answered in {time_taken}")

            player = get_current_player(session.get('username'))
            if player.player_name not in self.answered:
                self.answered.add(player.player_name)
                # score for this round = 30 seconds - time taken
                player.score += self.calculate_score(time_taken)
                db.session.add(player)
                db.session.commit()

    def on_clicked_button(self):
        """
        A button has been clicked by a user

        data will contain player name.
        """
        # get the player associated
        player = get_current_player(session.get('username'))
        if player is not None:
            # put in the answer queue
            self.answer_queue.put(player)

            # dequeue the first one
            first_player = self.answer_queue.get().get_dict()

            # dequeue the first person and emit to tv
            self.emit('player_clicked', first_player)

    def reset(self):
        """ helper method to reset everything """
        self.starting_time = time.time()
        self.answered = set()
        self.correct_answer_idx = -1
        self.correct_answer_text = None

    def calculate_score(self, time_taken):
        """ Return score the player would get based on the time taken to answer the question. """
        return int(30 - time_taken) * 7
