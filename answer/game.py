import time

from flask_socketio import Namespace
from flask import session

from answer.helpers import get_current_player
from answer.extensions import db


class Game(Namespace):
    """
    Queue the players according to who click the button the fastest.

    """
    # constants
    STATISTICS = "stats"

    # keep track of total players
    players_logged_in = set()

    # correct answer's index
    correct_answer_text = None
    correct_answer_idx = -1

    # starting time of the question
    starting_time = -1

    # players who answered
    answered = set()

    def on_connect(self):
        """ Return False if player does not have permission. Called when a player attempts to connect to the socket. """
        if session.get('username') is None:
            return False
        player = get_current_player(session.get('username'))
        if player is None:
            return False
        self.players_logged_in.add(player.get_name())

        self.emit(self.STATISTICS, self._get_stats())

    def on_disconnect(self):
        """ Called when a player disconnects from the socket. """
        player = get_current_player(session.get('username'))
        self.players_logged_in.discard(player.get_name())

        self.emit(self.STATISTICS, self._get_stats())

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
                player.score += self._calculate_score(time_taken)
                db.session.add(player)
                db.session.commit()

        self.emit(self.STATISTICS, self._get_stats())
    
    def add_score(self, player, amount):
        print("Player is adding score:", player, amount)
        if player is not None:
            player.score += amount
            db.session.add(player)
            db.session.commit()

    def reset(self):
        """ helper method to reset everything """
        self.starting_time = time.time()
        self.answered = set()
        self.correct_answer_idx = -1
        self.correct_answer_text = None

        self.emit(self.STATISTICS, self._get_stats())

    def _calculate_score(self, time_taken):
        """ Return score the player would get based on the time taken to answer the question. """
        return int(300 * (1 / 2) ** (time_taken / 18.927))

    def _get_stats(self):
        """ Returns the statistics of the game as dict. """
        return {
            "total_players": len(self.players_logged_in),
            "players": list(self.players_logged_in),
            "answered": list(self.answered)
        }
