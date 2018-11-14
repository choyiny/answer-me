from answer.extensions import db


class Player(db.Model):

    __tablename__ = "players"

    player_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    player_name = db.Column(db.Text, nullable=False)

    score = db.Column(db.BigInteger, default=0)

    def __init__(self, player_name):
        self.player_name = player_name

    def __repr__(self):
        return f"<Player {self.player_name}>"

    def get_dict(self):
        return {
            'name': self.player_name
        }
