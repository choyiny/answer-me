from answer.extensions import db


class Player(db.Model):

    __tablename__ = "players"

    player_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    player_name = db.Column(db.Text, nullable=False)

    nickname = db.Column(db.Text, unique=True)

    score = db.Column(db.BigInteger, default=0)

    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, player_name, nickname=None):
        self.player_name = player_name
        self.nickname = nickname
        self.score = 0
        self.is_admin = False

    def __repr__(self):
        return f"<Player {self.player_name}>"

    def get_dict(self):
        return {
            'name': self.get_name()
        }

    def get_name(self):
        return self.nickname or self.player_name
