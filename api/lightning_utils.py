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

            self.auth_header = self.get_login_token()
            return self.create_invoice(order_id, sats)

        else:
            print("Another thing happened")
            app.logger.error(f"Another thing happened status_code: {response_invoice.status_code}")

            return None

    def get_incoming_invoices(self):
        response_invoices_status = requests.get(
            lndhub_url + '/v2/invoices/incoming',
            headers = self.auth_header
        )

        if (response_invoices_status.status_code == 200):
            app.logger.info(f"get_invoices_status - 200 OK")

            json_response_invoices_status = response_invoices_status.json()
            print(json.dumps(json_response_invoices_status, indent=2))

            records_by_id = {record["payment_request"]: record for record in json_response_invoices_status}
            return records_by_id

        elif (response_invoices_status.status_code == 401):
            print("get_invoices_status - LndHub API error. Probably the token expired!")
            app.logger.info(f"LndHub API error. Probably the token expired!")

            self.auth_header = self.get_login_token()
            return self.get_invoices_status()

        else:
            print("Another thing happened")
            app.logger.error(f"get_invoices_status - Another thing happened status_code: {response_invoices_status.status_code}")
            return None
