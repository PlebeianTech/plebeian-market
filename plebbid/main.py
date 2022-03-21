from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

import jwt
import logging

class MyFlask(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.initialized = False

    def __call__(self, environ, start_response):
        if not self.initialized:
            from plebbid.controllers import api_blueprint
            app.register_blueprint(api_blueprint)
            self.initialized = True
        return super().__call__(environ, start_response)

app = MyFlask(__name__)
app.config.from_object('plebbid.config')

db = SQLAlchemy(app)

from plebbid import models as m

@app.cli.command("create-db")
@with_appcontext
def create_db():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'success': False, 'message': "Missing token."}), 400
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = m.Buyer.query.filter_by(key=data['user_key']).first()
        except Exception:
           return jsonify({'success': False, 'message': "Invalid token."})
        return f(current_user, *args, **kwargs)
    return decorator

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
