import json
from typing import Optional, Dict
from meapi.credentials_managers import CredentialsManager


class RedisCredentialsManager(CredentialsManager):
    """
    Redis Credentials Manager.
        - This class is used to store the credentials in a redis cache.

    Parameters:
        - redis: (``redis.Redis``) The redis object of redis-py library. (https://github.com/redis/redis-py)

    Examples:
        >>> from meapi import Me
        >>> from redis import Redis
        >>> from meapi.credentials_managers.redis import RedisCredentialsManager
        >>> redis = Redis(host='localhost', port=6379, db=0)
        >>> rcm = RedisCredentialsManager(redis)
        >>> me = Me(phone_number=972123456789, credentials_manager=rcm)


    """
    def __init__(self, redis):
        super().__init__()
        self.redis = redis

    def get(self, phone_number: str) -> Optional[Dict[str, str]]:
        data = self.redis.get(str(phone_number))
        if data:
            return json.loads(data)
        return None

    def set(self, phone_number: str, data: Dict[str, str]):
        self.redis.set(str(phone_number), json.dumps(data))

    def update(self, phone_number: str, access_token: str):
        existing_content = json.loads(self.redis.get(str(phone_number)))
        existing_content['access'] = access_token
        self.redis.set(str(phone_number), json.dumps(existing_content))

    def delete(self, phone_number: str):
        self.redis.delete(str(phone_number))


