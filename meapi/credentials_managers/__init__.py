import logging
from abc import abstractmethod, ABC
from typing import Optional, Dict


class CredentialsManager(ABC):
    """
    Abstract class for credentials managers.
        - You can implement your own credentials manager to store credentials in your own way.
    """

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get(self, phone_number: str) -> Optional[Dict[str, str]]:
        """
        Get the credentials by ``phone_number`` key.

        :param phone_number: The phone number of the client.
        :type phone_number: ``str``
        :return: Optional dict with the credentials. see example below.
        :rtype: dict

        Example for return value::

            {
                'access': 'xxx',
                'refresh': 'xxx',
                'pwd_token': 'xxx'
            }
        """
        pass

    @abstractmethod
    def set(self, phone_number: str, data: Dict[str, str]):
        """
        Set the credentials by ``phone_number`` key.

        :param phone_number: The phone number of the client.
        :type phone_number: str
        :param data: Dict with credentials. see example below.
        :type data: dict

        Example for ``data``::

            {
                'access': 'xxx',
                'refresh': 'xxx',
                'pwd_token': 'xxx',
            }
        """
        pass

    @abstractmethod
    def update(self, phone_number: str, access_token: str):
        """
        Update the access token in the credentials by ``phone_number`` key.

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
