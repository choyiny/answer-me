from flask import Flask, request, render_template

from answer import config
from answer.extensions import db
from answer.helpers import gen_response


# initialize app with config params
app = Flask(__name__)
app.config.from_object(config)

# initialize connection to db
with app.app_context():
    # initialize connection to db
    db.init_app(app)

    # # Create all required models for database
    # from answer.models.player import Player
    # db.create_all()


@app.route("/")
def index():
    return gen_response({"success": True})
