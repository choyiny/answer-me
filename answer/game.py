from queue import Queue

from flask_socketio import Namespace

from answer.models import Player


class Game(Namespace):
    """
    Queue the players according to who click the button the fastest.

    """
    answer_queue = Queue()

    def on_clicked_button(self, data):
        """
        A button has been clicked by a user

        data will contain email.
        """
        print(data)
        print('player clicked button')
        # get the player associated
        if data.get('email'):
            player = Player.query.filter_by(player_email=data.get('email')).first()
            if player is not None:
                # put in the answer queue
                self.answer_queue.put(player)

                # dequeue the first one
                first_player = self.answer_queue.get().get_dict()

                # dequeue the first person and emit to tv
                self.emit('player_clicked', first_player)
