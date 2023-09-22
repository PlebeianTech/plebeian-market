import requests, json
import models as m
import time
from extensions import db
from flask import current_app as app

auth_header = ''
lndhub_url = ''

class LightningInvoiceUtil:
    def __init__(self):
        self.lndhub_url = app.config['LNDHUB_URL']
        app.logger.info(f"init  - LNDHUB_URL={self.lndhub_url}")
        self.auth_header = self.get_login_token()

    def get_login_token(self):
        app.logger.info(f"get_login_token - Trying login to LndHub API ({self.lndhub_url})...")

        payload = {
            'login': app.config['LNDHUB_USER'],
            'password': app.config['LNDHUB_PASSWORD']
        }

        r = requests.post(
            self.lndhub_url + '/auth',
            data=payload
        )

        json_res = r.json()
        app.logger.debug(f"get_login_token - json_res = ({json_res})...")

        if 'error' in json_res:
            app.logger.error(f"get_login_token - {json_res['message']}")
            time.sleep(60)
            return False

        access_token = json_res['access_token']
        app.logger.info(f"get_login_token - Access token = {access_token}")

        headers = {"Authorization": "Bearer " + access_token}

        return headers

    def create_invoice(self, order_id, sats):
        payload = {
            'amount':sats,
            'description':'Payment for Order #' + str(order_id)
        }
        app.logger.debug(f"Creating invoice for order: {payload}")

        response_invoice = requests.post(
            self.lndhub_url + '/v2/invoices',
            headers = self.auth_header,
            json=payload
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
            self.lndhub_url + '/v2/invoices/incoming',
            headers = self.auth_header
        )

        if (response_invoices_status.status_code == 200):
            app.logger.info(f"get_invoices_status - 200 OK")

            json_response_invoices_status = response_invoices_status.json()
            # print(json.dumps(json_response_invoices_status, indent=2))

            records_by_id = {record['payment_request']: record for record in json_response_invoices_status}
            return records_by_id

        elif (response_invoices_status.status_code == 401):
            print("get_invoices_status - LndHub API error. Probably the token expired!")
            app.logger.info(f"LndHub API error. Probably the token expired!")

            self.auth_header = self.get_login_token()
            return self.get_incoming_invoices()

        else:
            print("Another thing happened")
            app.logger.error(f"get_invoices_status - Another thing happened status_code: {response_invoices_status.status_code}")
            return None

    def pay_to_ln_address(self, ln_address, amount, comment):
        return self.get_ln_invoice_from_ln_address(ln_address, amount, comment)

    def get_ln_invoice_from_ln_address(self, ln_address, amount, comment):
        alby_lnaddress_proxy_url = 'https://lnaddressproxy.getalby.com/generate-invoice?'

        if not ln_address:
            app.logger.error(f"get_ln_invoice_from_ln_address - No ln_address provided")
            return False

        if not amount:
            app.logger.error(f"get_ln_invoice_from_ln_address - No amount_sats provided ln_address={ln_address}")
            return False

        amount *= 1000      # amount is sats, but here millisats are required

        alby_lnaddress_proxy_url += 'ln=' + ln_address + '&amount=' + amount

        if comment:
            alby_lnaddress_proxy_url += '&comment=' + comment

        app.logger.info(f"get_ln_invoice_from_ln_address - Making request to Alby proxy ({alby_lnaddress_proxy_url}) ...")
        r = requests.get(alby_lnaddress_proxy_url)

        json_res = r.json()
        app.logger.info(f"get_ln_invoice_from_ln_address - response from Alby: {json_res}")

        if 'error' in json_res:
            app.logger.error(f"get_ln_invoice_from_ln_address - {json_res}")
            return False

        try:
            ln_invoice = json_res['invoice']['pr']
            app.logger.info(f"get_ln_invoice_from_ln_address - ln_invoice = {ln_invoice}")

        except:
            app.logger.error(f"get_ln_invoice_from_ln_address - Error getting the ln invoice from the response")
            return False

        return ln_invoice
