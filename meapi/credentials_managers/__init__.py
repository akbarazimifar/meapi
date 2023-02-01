import logging
from abc import abstractmethod, ABC
from typing import Optional, Dict


class CredentialsManager(ABC):
    """
    Abstract class for credentials managers.
        - You can implement your own credentials manager to store credentials in your own way.
    """
    @abstractmethod
    def get(self, phone_number: str) -> Optional[Dict[str, str]]:
        """
        Get the credentials by ``phone_number`` key.
            - If the credentials are not in the manager, return ``None``.
            - The keys of the dict must be: ``access``, ``refresh`` and ``pwd_token``, see example below.

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
            - If the credentials are already in the manager, update them.

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
            - If the credentials are not in the manager, do nothing.
            - You can implement your own idea of what ``delete`` means (e.g. change the state of your credentials).
        """
        pass
