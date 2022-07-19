import logging
import os.path
from abc import ABC, abstractmethod
from json import load, JSONDecodeError, dump, dumps, loads
from typing import Optional
from meapi.utils.exceptions import MeException

_logger = logging.getLogger(__name__)


class CredentialsManager(ABC):
    """
    Abstract class for credentials managers.
        - You can implement your own credentials manager to store credentials in your own way.
    """

    @abstractmethod
    def get(self, phone_number: str) -> Optional[dict]:
        """
        Get the credentials by ``client.phone_number`` key.

        :param phone_number: The phone number of the client.
        :type phone_number: ``str``
        :return: Dict with credentials. ``None`` if credentials are not found for the given ``phone_number``. see example below.
        :rtype: dict

        Example for return value::

            {
                'access': 'xxx',
                'refresh': 'xxx',
                'pwd_token': 'xxx',
                'uuid': 'xxxx'
            }
        """
        pass

    @abstractmethod
    def set(self, phone_number: str, data: dict):
        """
        Store new credentials with ``phone_number`` key.
        
        :param phone_number: The phone number of the client.
        :type phone_number: str
        :param data: Dict with credentials. see example below.
        :type data: dict

        Example for ``data``::

            {
                'access': 'xxx',
                'refresh': 'xxx',
                'pwd_token': 'xxx',
                'uuid': 'xxxx'
            }
        """
        pass

    @abstractmethod
    def update(self, phone_number: str, access_token: str):
        """
        Update the access token in the credentials with ``phone_number`` key.
        
        :param phone_number: The phone number of the client.
        :type phone_number: str
        :param access_token: The new access token.
        :type access_token: str
        """
        pass

    @abstractmethod
    def delete(self, phone_number: str):
        """
        Delete the credentials by ``phone_number`` key.
        """
        pass


class JsonFileCredentialsManager(CredentialsManager):
    """
    Json File Credentials Manager
        - This class is used to store the credentials in a json file.

    Parameters:
        - config_file: (``str``) The config file path. *Default:* 'config.json'.
    """
    def __init__(self, config_file: str = 'config.json'):
        if str(config_file).endswith(".json"):
            self.config_file = config_file
        else:
            _logger.warning(f"The config file is not a json file. Defaulting to 'config.json'.")
            self.config_file = 'config.json'

    def _read_or_create(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as config_file:
                try:
                    existing_content = load(config_file)
                except JSONDecodeError:
                    raise MeException("Not a valid json file: " + self.config_file)
        else:
            with open(self.config_file, "w") as new_config_file:
                new_config_file.write('{}')
                existing_content = {}
        return existing_content

    def get(self, phone_number: str) -> Optional[dict]:
        existing_content = self._read_or_create()
        if not existing_content.get(str(phone_number)):
            return None
        else:
            return existing_content[str(phone_number)]

    def set(self, phone_number: str, data: dict):
        existing_content = self._read_or_create()
        existing_content[str(phone_number)] = data
        with open(self.config_file, "w") as config_file:
            dump(existing_content, config_file, indent=4, sort_keys=True)

    def update(self, phone_number: str, access_token: str):
        existing_content = self._read_or_create()
        existing_content[str(phone_number)]['access'] = access_token
        with open(self.config_file, "w") as config_file:
            dump(existing_content, config_file, indent=4, sort_keys=True)

    def delete(self, phone_number: str):
        existing_content = self._read_or_create()
        if existing_content.get(str(phone_number)):
            del existing_content[str(phone_number)]
            with open(self.config_file, "w") as config_file:
                dump(existing_content, config_file, indent=4, sort_keys=True)


class RedisCredentialsManager(CredentialsManager):
    """
    Redis Credentials Manager.
        - This class is used to store the credentials in a redis cache.
    """
    def __init__(self, redis):
        self.redis = redis

    def get(self, phone_number: str) -> Optional[dict]:
        data = self.redis.get(str(phone_number))
        if data:
            return loads(data)
        return None

    def set(self, phone_number: str, data: dict):
        self.redis.set(str(phone_number), dumps(data))

    def update(self, phone_number: str, access_token: str):
        existing_content = loads(self.redis.get(str(phone_number)))
        existing_content['access'] = access_token
        self.redis.set(str(phone_number), dumps(existing_content))

    def delete(self, phone_number: str):
        self.redis.delete(str(phone_number))

