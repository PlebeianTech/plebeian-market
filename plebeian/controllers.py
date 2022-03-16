from flask import Blueprint, jsonify, render_template, session

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')
