import json
from typing import Optional
from meapi.credentials_managers.credentials_manager import CredentialsManager


class RedisCredentialsManager(CredentialsManager):
    """
    Redis Credentials Manager.
        - This class is used to store the credentials in a redis cache.

    Parameters:
        - redis: (``redis.Redis``) The redis object of redis-py library. (https://github.com/redis/redis-py)
    """
    def __init__(self, redis):
        super().__init__()
        self.redis = redis

    def get(self, phone_number: str) -> Optional[dict]:
        data = self.redis.get(str(phone_number))
        if data:
            return json.loads(data)
        return None

    def set(self, phone_number: str, data: dict):
        self.redis.set(str(phone_number), json.dumps(data))

    def update(self, phone_number: str, access_token: str):
        existing_content = json.loads(self.redis.get(str(phone_number)))
        existing_content['access'] = access_token
        self.redis.set(str(phone_number), json.dumps(existing_content))

    def delete(self, phone_number: str):
        self.redis.delete(str(phone_number))


