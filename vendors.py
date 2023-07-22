import datetime
import json
import requests

from data_service import DataService

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


class RamiLevyOrders:
    LOGIN_URL = 'https://api-prod.rami-levy.co.il/api/v2/site/auth/login'
    ORDER_URL = 'https://api-prod.rami-levy.co.il/api/v3/site/orders/'
    DATETIME_STR_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    START_DATE = datetime.datetime(2023, 3, 1)

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token = None
        self._products = []

    def login(self):
        login_url = self.LOGIN_URL
        options_response = requests.options(login_url)
        if options_response.status_code == 200:
            formdata = {
                "username": self._username,
                "password": self._password
            }
            login_response = requests.post(login_url, data=formdata)
            if login_response.status_code == 200:
                self._token = login_response.json()["user"]["token"]
                return login_response.json()

    def get_relevant_orders(self):
        login_response = self.login()
        first_time = False
        if login_response:
            old_orders = json.loads(DataService.get_data())
            if not old_orders:
                first_time = True
            last_order = max(
                {datetime.datetime.strptime(p["created_at"], self.DATETIME_STR_FORMAT) for p in
                 old_orders}) if old_orders else None
            relevant_orders = [order for order in login_response["user"]["orders"] if
                               self.is_relevant(order, last_order, first_time)]
            return relevant_orders
        return []

    def collect_orders(self):
        orders = self.get_relevant_orders()
        for order in orders:
            self.collect_order(order["id"])
        DataService.update_data(self._products)
        logger.info(f"Updated {len(self._products)} products")

    def collect_order(self, order_id):
        order_url = self.ORDER_URL + str(order_id)
        options_response = requests.options(order_url)
        if options_response.status_code == 200:
            headers = {
                'Ecomtoken': self._token
            }
            order_response = requests.get(order_url, headers=headers)
            if order_response.status_code == 200:
                data = order_response.json()["data"]
                lines = data["lines"]
                for line in lines:
                    line["created_at"] = data["created_at"]
                self._products += lines
        else:
            logger.error(options_response.status_code)

    def is_relevant(self, order: dict, last_order: datetime, first_time=False):
        order_date = datetime.datetime.strptime(order["created_at"], self.DATETIME_STR_FORMAT)
        if first_time:
            return order_date > self.START_DATE
        return order_date > last_order
