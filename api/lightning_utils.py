import requests, json
import models as m
from main import app
from extensions import db

lndhub_url = 'https://ln.getalby.com'
auth_header = ''

class LightningInvoiceUtil:
    def __init__(self):
        self.auth_header = self.get_login_token()

    def get_login_token(self):
        app.logger.info(f"LndHub API error. Probably the token expired!")

        payload = {
            'login': app.config['LNDHUB_USER'],
            'password': app.config['LNDHUB_PASSWORD']
        }

        r = requests.post(
            lndhub_url + '/auth',
            data=payload
        )

        json_res = r.json()
        access_token = json_res['access_token']
        #print('Access token: ', access_token)

        headers = {"Authorization": "Bearer " + access_token}

        return headers

    def create_invoice(self, order_id, sats):
        payload = {
            'amount':sats,
            'description':'Payment for Order #' + order_id
        }

        response_invoice = requests.post(
            lndhub_url + '/v2/invoices',
            headers = self.auth_header,
            data=payload
        )

        if (response_invoice.status_code == 200):
            print("The request to create a new LN invoice was a success!")
            app.logger.info(f"The request to create a new LN invoice was a success!")

            json_response_invoice = response_invoice.json()
            print(json.dumps(json_response_invoice, indent=2))
            app.logger.debug(f"The request to create a new LN invoice was a success!")

            payment_hash = json_response_invoice['payment_hash']
            invoice = json_response_invoice['payment_request']
            expires_at = json_response_invoice['expires_at']

            lightning_invoice = m.LightningInvoice(
                order_id=order_id,
                invoice=invoice,
                payment_hash=payment_hash,
                price=sats,
                expires_at=expires_at         # "2023-08-03T08:52:07.473598061Z"
            )
            db.session.add(lightning_invoice)
            db.session.commit()

            return json_response_invoice

        elif (response_invoice.status_code == 401):
            print("LndHub API error. Probably the token expired!")
            app.logger.info(f"LndHub API error. Probably the token expired!")

            auth_header = self.get_login_token()
            return self.create_invoice(order_id, sats)

        else:
            print("Another thing happened")
            app.logger.error(f"Another thing happened status_code: {response_invoice.status_code}")

            return None
