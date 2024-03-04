from datetime import datetime, timedelta
import requests
from flask import current_app as app

auth_header = ''
lndhub_url = ''

class LndHubClient:
    def __init__(self):
        self.lndhub_url = app.config['LNDHUB_URL']
        app.logger.debug(f"init - LNDHUB_URL={self.lndhub_url}")
        login_token = self.get_login_token()

        if not login_token:
            app.logger.error(f"__init__ - Couldn't get the login_token ({self.lndhub_url})...")
            return false

        self.auth_header = login_token

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
            app.logger.error(f"get_login_token - error while trying to get the login_token from the LndHub: {json_res['error']}")
            return False

        access_token = json_res['access_token']
        app.logger.info(f"get_login_token - Access token = {access_token}")

        return {"Authorization": "Bearer " + access_token}

    def create_invoice(self, order_uuid, sats):
        payload = {
            'amount': sats,
            'description': f"Payment for Order #{order_uuid}"
        }
        app.logger.debug(f"create_invoice - Creating invoice for order: {payload}")

        response_invoice = requests.post(
            self.lndhub_url + '/v2/invoices',
            headers = self.auth_header,
            json=payload
        )

        if (response_invoice.status_code == 200):
            app.logger.info(f"create_invoice - The request to create a new LN invoice was a great success!")
            return response_invoice.json()

        elif (response_invoice.status_code == 401):
            app.logger.info(f"create_invoice - LndHub API error 401. Probably the token expired!")
            return False

        else:
            app.logger.error(f"create_invoice - Another thing happened status_code: {response_invoice.status_code}")
            return False

    def get_incoming_invoices(self):
        response_invoices_status = requests.get(
            self.lndhub_url + '/v2/invoices/incoming',
            headers = self.auth_header
        )

        if (response_invoices_status.status_code == 200):
            app.logger.debug(f"get_incoming_invoices - 200 OK")
            return {record['payment_request']: record for record in response_invoices_status.json()}

        elif (response_invoices_status.status_code == 401):
            app.logger.info(f"get_incoming_invoices - LndHub API error 401. Probably the token expired!")
            return False

        else:
            app.logger.error(f"get_incoming_invoices - Another thing happened status_code: {response_invoices_status.status_code}")
            return False

    def pay_to_ln_address(self, ln_address, amount, comment):
        ln_invoice = self.get_ln_invoice_from_ln_address(ln_address, amount, comment)

        if not ln_invoice:
            return False

        payload = {
            'amount':amount,
            'invoice':ln_invoice
        }
        app.logger.info(f"pay_to_ln_address - payload: {payload}")

        response_invoice = requests.post(
            self.lndhub_url + '/v2/payments/bolt11',
            headers = self.auth_header,
            json=payload
        )

        if (response_invoice.status_code == 200):
            app.logger.info(f"pay_to_ln_address - The request to pay a LN address ({ln_address} - {amount} sats) was a success!")

            json_response_invoice = response_invoice.json()
            app.logger.debug(f"pay_to_ln_address - ****************** {json_response_invoice}")

            return json_response_invoice

        elif (response_invoice.status_code == 400 or response_invoice.status_code == 401):
            app.logger.info(f"pay_to_ln_address - LndHub API error 400. Probably the token expired! {response_invoice.json()}")
            return False

        else:
            app.logger.error(f"pay_to_ln_address - Another thing happened status_code: {response_invoice.status_code}")
            return False

    def get_ln_invoice_from_ln_address(self, ln_address, amount, comment):
        alby_lnaddress_proxy_url = 'https://api.getalby.com/lnurl/generate-invoice?'

        if not ln_address:
            app.logger.error(f"get_ln_invoice_from_ln_address - No ln_address provided")
            return False

        if not amount:
            app.logger.error(f"get_ln_invoice_from_ln_address - No amount_sats provided ln_address={ln_address}")
            return False

        amount *= 1000      # amount is sats, but here millisats are required

        alby_lnaddress_proxy_url += 'ln=' + ln_address + '&amount=' + str(amount)

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

class MockLndHubClient:
    def __init__(self):
        return None

    def get_login_token(self):
        return None

    def create_invoice(self, _order_uuid, _sats):
        return {'payment_request': "MOCK_PAYMENT_REQUEST", 'payment_hash': "MOCK_PAYMENT_HASH", 'expires_at': datetime.utcnow() + timedelta(minutes=10)}

    def get_incoming_invoices(self):
        return None

    def pay_to_ln_address(self, ln_address, amount, comment):
        return None

    def get_ln_invoice_from_ln_address(self, ln_address, amount, comment):
        return None
