from datetime import datetime
from threading import Thread
import time

from flask import Flask
from flask_socketio import SocketIO, emit, disconnect

from lndgrpc import LNDClient

class MyFlask(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.initialized = False

    def __call__(self, environ, start_response):
        if not self.initialized:
            from plebeian.controllers import main_blueprint
            app.register_blueprint(main_blueprint)
            self.initialized = True
        return super().__call__(environ, start_response)

app = MyFlask(__name__)
app.config.from_object('config')

socketio = SocketIO(app)

def worker():
    print("Started worker...")
    seen_invoices = set()
    while True:
        time.sleep(5)
        client = LNDClient("plebeian.m.voltageapp.io:10009", macaroon_filepath="admin.macaroon", cert_filepath="tls.cert")
        resp = client.list_invoices()
        for invoice in resp.invoices:
            if invoice.payment_request not in seen_invoices and invoice.settled:
                seen_invoices.add(invoice.payment_request)
                socketio.emit('bid', {'amount': invoice.amt_paid_sat}, namespace='/auction')

Thread(target=worker).start()
