from datetime import datetime

from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
