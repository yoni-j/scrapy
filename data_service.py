import os

import redis
from typing import List
import json


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

KEY = "products"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True)


class DataService:
    @staticmethod
    def update_data(new_data: List[dict], replace=False):
        current_data = json.loads(DataService.get_data())
        if not replace:
            new_data = current_data + new_data
        r.set(KEY, json.dumps(new_data, ensure_ascii=False))

    @staticmethod
    def get_data() -> str:
        return r.get(KEY) or '[]'
