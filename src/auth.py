import asyncio
import datetime
import json
import os
import time
import aiohttp

from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from etl_service import OrderItem


class RamiLevy:
    BASE_URL = 'https://www.rami-levy.co.il/'
    ORDERS_URL = "https://www-api.rami-levy.co.il/api/v3/site/orders/"

    def __init__(self):
        self._orders = []
        self._headers = {}
        self._items = []

    def run(self):
        return self.collect_orders()

    def _login(self):
        options = {
            'disable_encoding': True
        }
        driver = webdriver.Chrome(seleniumwire_options=options)
        driver.get(f"{self.BASE_URL}/he")
        login_div = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'login-user')))
        login_div.click()
        time.sleep(2)
        username_field = driver.find_element(By.ID, 'email')
        password_field = driver.find_element(By.ID, 'password')
        username_field.send_keys(os.getenv("USER1"))
        password_field.send_keys(os.getenv("PASSWORD1"))
        submit_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='כניסה']")
        submit_button.click()
        time.sleep(6)
        for request in driver.requests:
            if "site/auth/login" in request.url:
                auth_token = request.headers.get('authorization')
                body = json.loads(request.response.body)
                user_token = body["user"]["token"]
                self._orders = body["user"]["orders"]
                self._headers = {
                    'Ecomtoken': user_token,
                    'Authorization': auth_token
                }
        driver.quit()

    async def collect_orders(self) -> list:
        self._login()
        tasks = []
        for order in self._orders:
            tasks.append(self._collect_order(order["id"]))
        await asyncio.gather(*tasks)
        return self._items

    async def _collect_order(self, order_id):
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.options(f"{self.ORDERS_URL}{order_id}") as options_resp:
                if options_resp.status in [200, 204]:
                    async with session.get(f"{self.ORDERS_URL}{order_id}") as resp:
                        if resp.status in [200, 204]:
                            data = await resp.json()
                            order_id = data["data"]["id"]
                            order_date = datetime.datetime.strptime(data["data"]["supply_at"], "%Y-%m-%d %H:%M:%S")
                            for line in data["data"]["lines"]:
                                self._items.append(OrderItem(order_id=order_id, order_date=order_date,
                                                             item_name=line["name"], item_id=line["item_id"],
                                                             price=float(line["price"]), quantity=line["quantity"]))


def get_list():
    data = asyncio.run(RamiLevy().collect_orders())
    data_json = [dict(product) for product in data]
    return data_json
