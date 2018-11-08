from answer.extensions import db


class Player(db.Model):

    __tablename__ = "players"

    player_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    player_email = db.Column(db.Text, nullable=False)

    score = db.Column(db.BigInteger, default=0)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return f"<Player {self.email}>"
