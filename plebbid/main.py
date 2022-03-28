from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import lndgrpc
import logging

class MyFlask(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.initialized = False

    def __call__(self, environ, start_response):
        if not self.initialized:
            from plebbid.api import api_blueprint
            app.register_blueprint(api_blueprint)
            self.initialized = True
        return super().__call__(environ, start_response)

app = MyFlask(__name__)
app.config.from_object('plebbid.config')

CORS(app)

db = SQLAlchemy(app)

from plebbid import models as m

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
    from plebbid import api_tests
    suite = unittest.TestLoader().loadTestsFromModule(api_tests)
    unittest.TextTestRunner().run(suite)

@app.cli.command("settle-bids")
@with_appcontext
def settle_bids():
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

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
        if not token:
            return jsonify({'success': False, 'message': "Missing token."}), 400
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = m.Buyer.query.filter_by(key=data['user_key']).first()
        except Exception:
           return jsonify({'success': False, 'message': "Invalid token."})
        return f(current_user, *args, **kwargs)
    return decorator

class MockLNDClient():
    class InvoiceResponse():
        def __init__(self):
            self.payment_request = 'MOCK_REQUEST'

    def add_invoice(self, value):
        return MockLNDClient.InvoiceResponse()

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
        lnurl.encode(app.config['BASE_URL']) # try parsing again to check that teh patch worked
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
