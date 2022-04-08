from datetime import datetime
from functools import wraps
import os
import random
import signal
import string
import sys
import time

from flask import Flask, jsonify, request, send_file
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import lndgrpc
import logging

class MyFlask(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.initialized = False

    def __call__(self, environ, start_response):
        if not self.initialized:
            from server.api import api_blueprint
            app.register_blueprint(api_blueprint)
            self.initialized = True
        return super().__call__(environ, start_response)

app = MyFlask(__name__, static_folder="../client/static")
app.config.from_object('server.config')

CORS(app)

db = SQLAlchemy(app)

from server import models as m

@app.cli.command("create-db")
@with_appcontext
def create_db():
    db.create_all()
    db.session.add(m.State(last_settle_index=0))
    db.session.commit()

@app.cli.command("run-tests")
@with_appcontext
def run_tests():
    import unittest
    from server import api_tests
    suite = unittest.TestLoader().loadTestsFromModule(api_tests)
    unittest.TextTestRunner().run(suite)

@app.cli.command("settle-bids")
@with_appcontext
def settle_bids():
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))
    lnd = get_lnd_client()
    last_settle_index = db.session.query(m.State).first().last_settle_index
    for invoice in lnd.subscribe_invoices(): # TODO: use settle_index after merged in lnd-grpc-client
        if invoice.state == lndgrpc.client.ln.SETTLED and invoice.settle_index > last_settle_index:
            bid = db.session.query(m.Bid).filter_by(payment_request=invoice.payment_request).first()
            if bid:
                state = db.session.query(m.State).first()
                state.last_settle_index = invoice.settle_index
                bid.settled_at = datetime.utcnow()
                db.session.commit()
                app.logger.info(f"Settled bid {bid.id} amount {bid.amount}.")

def get_token_from_request():
    return request.headers.get('X-Access-Token')

def get_user_from_token(token):
    if not token:
        return None

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except Exception:
        return None

    return m.User.query.filter_by(key=data['user_key']).first()

def user_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'success': False, 'message': "Missing token."}), 401
        user = get_user_from_token(token)
        if not user:
            return jsonify({'success': False, 'message': "Invalid token."}), 401
        return f(user, *args, **kwargs)
    return decorator

class MockLNDClient():
    class InvoiceResponse():
        def __init__(self, payment_request=None, state=None, settle_index=None):
            if payment_request:
                self.payment_request = payment_request
            else:
                self.payment_request = "MOCK_" + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
            self.state = state
            self.settle_index = settle_index

    def add_invoice(self, value):
        return MockLNDClient.InvoiceResponse()

    def subscribe_invoices(self):
        last_settle_index = db.session.query(m.State).first().last_settle_index
        while True:
            time.sleep(3)
            for unsettled_bid in db.session.query(m.Bid).filter(m.Bid.settled_at == None):
                last_settle_index += 1
                yield MockLNDClient.InvoiceResponse(unsettled_bid.payment_request, lndgrpc.client.ln.SETTLED, last_settle_index)

def get_lnd_client():
    if app.config['MOCK_LND']:
        return MockLNDClient()
    else:
        return lndgrpc.LNDClient(app.config['LND_GRPC'], macaroon_filepath=app.config['LND_MACAROON'], cert_filepath=app.config['LND_TLS_CERT'])

if __name__ == '__main__':
    import lnurl
    try:
        lnurl.encode(app.config['BASE_URL'])
    except lnurl.exceptions.InvalidUrl:
        # HACK: allow URLs with http:// and no TLD in development mode (http://localhost)
        from pydantic import AnyHttpUrl
        class ClearnetUrl(AnyHttpUrl):
            pass
        app.logger.warning("Patching lnurl.types.ClearnetUrl!")
        lnurl.types.ClearnetUrl = ClearnetUrl
        lnurl.encode(app.config['BASE_URL']) # try parsing again to check that the patch worked

    @app.route('/app', strict_slashes=False, methods=['GET'])
    def index():
        return send_file("../client/app/index.html")

    @app.route('/app/auction', strict_slashes=False, methods=['GET'])
    def auction():
        return send_file("../client/app/auction/index.html")

    @app.route('/app/bundle.js', methods=['GET'])
    def bundle():
        return send_file("../client/app/bundle.js")

    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
