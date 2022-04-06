from flask import Blueprint, render_template

from plebeianmarket.main import app

web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/app', methods=['GET'])
def index():
    return render_template("app.html", config=app.config)
