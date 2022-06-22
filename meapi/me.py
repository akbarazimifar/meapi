from json import loads, JSONDecodeError
from re import match
from typing import Union
import requests
from meapi.account import Account
from meapi.auth import Auth
from meapi.exceptions import MeException, MeApiException
from meapi.helpers import valid_phone_number
from meapi.notifications import Notifications
from meapi.settings import Settings
from meapi.social import Social

ME_BASE_API = 'https://app.mobile.me.app'


class Me(Auth, Account, Social, Settings, Notifications):
    """
    Create a new instance to interact with MeAPI. **See** `Authentication <https://meapi.readthedocs.io/en/latest/setup.html#authentication>`_ **for more information.**

    :param phone_number: International phone number format. Required on the `Unofficial method <https://meapi.readthedocs.io/en/latest/setup.html#unofficial-method>`_. Default: ``None``.
    :type phone_number: Union[str, int, None]
    :param activation_code: You can provide the ``activation_code`` from Me in advance, without the need for a prompt. Default = ``None``.
    :type activation_code: Union[int, str, None]
    :param access_token: Official access token, Required on the `Official method <https://meapi.readthedocs.io/en/latest/setup.html#official-method>`_. Default: ``None``.
    :type access_token: Union[str, None]
    :param config_file: Path to credentials json file. Default: ``config.json``.
    :type config_file: Union[str, None]
    :param proxies: Dict with proxy configuration. Default: ``None``.
    :type proxies: dict
    :param account_details: You can provide all login details can be provided in dict format, designed for cases of new account registration without the need for a prompt. Default: ``None``
    :type account_details: dict

    Example for ``account_details``::

        {
            'phone_number': 972123456789, # Required always
            'activation_code': 123456, # Required only for the first time
            'first_name': 'Regina', # Required for first account registration
            'last_name': 'Phalange', # Optional for first account registration
            'email': 'kenadams@friends.tv', # Optional for first account registration
            'upload_random_data': True # Recommended for first account registration. Default: True
        }
    """
    def __init__(self,
                 phone_number: Union[int, str, None] = None,
                 activation_code: Union[int, str, None] = None,
                 access_token: Union[str, None] = None,
                 account_details: dict = None,
                 config_file: Union[str, None] = 'config.json',
                 proxies: dict = None):
        if config_file.endswith(".json"):
            self.config_file = config_file
        else:
            print("Not a valid config json file. Using default 'config.json' file.")
            self.config_file = 'config.json'

        if not access_token and not phone_number and not account_details:
            raise MeException("You need to provide phone number, account details or access token!")
        if access_token and phone_number:
            raise MeException("Access-token mode does not accept phone number, just access token.")
        if account_details and (phone_number or access_token):
            raise MeException("No need to provide phone number or access token if account_detail provided.")

        if account_details:
            if not isinstance(account_details, dict):
                raise MeException("Account details must be data dict. ")
            if account_details.get('phone_number') and account_details.get('activation_code'):
                phone_number = account_details['phone_number']
                if match(r'^\d{6}$', str(account_details['activation_code'])):
                    activation_code = account_details['activation_code']
                else:
                    raise MeException("Not a valid 6-digits activation code!")

        self.phone_number = valid_phone_number(phone_number) if phone_number else phone_number
        self.activation_code = activation_code
        self.access_token = access_token
        self.account_details = account_details
        self.uuid = None
        self.proxies = proxies

        if not self.access_token:
            auth_data = self.credentials_manager()
            if auth_data:
                self.access_token = auth_data['access']

    def __repr__(self):
        return f"<Me phone={self.phone_number} uuid={self.uuid}>"

    def __str__(self):
        return str(self.phone_number)

    def _make_request(self,
                      req_type: str,
                      endpoint: str,
                      body: dict = None,
                      headers: dict = None,
                      ) -> Union[dict, list]:
        """
        Make request to Me api and return the response.

        :param req_type: HTTP request type: ``post``, ``get``, ``put``, ``patch``, ``delete``.
        :type req_type: str
        :param endpoint: api endpoint.
        :type endpoint: str
        :param body: The body of the request. Default: ``None``.
        :type body: dict
        :param headers: Use different headers instead of the default.
        :type headers: dict
        :raises MeApiException: If HTTP status is bigger than ``400``.
        :return: API response as dict or list.
        :rtype: Union[dict, list]
        """
        getattr(requests, 'post')
        url = ME_BASE_API + endpoint
        request_types = ['post', 'get', 'put', 'patch', 'delete']
        if req_type not in request_types:
            raise MeException("Request type not in requests type list!!\nAvailable types: " + ", ".join(request_types))
        if headers is None:
            headers = {'accept-encoding': 'gzip', 'user-agent': 'okhttp/4.9.1',
                       'content-type': 'application/json; charset=UTF-8'}
        max_rounds = 3
        while max_rounds != 0:
            max_rounds -= 1
            headers['authorization'] = self.access_token
            response = getattr(requests, req_type)(url=url, json=body, headers=headers, proxies=self.proxies)
            try:
                response_text = loads(response.text)
            except JSONDecodeError:
                raise MeException(f"The response (Status code: {response.status_code}) received does not contain a valid JSON:\n" + str(response.text))
            if response.status_code == 403 and self.phone_number:
                self.generate_access_token()
                continue

            if response.status_code >= 400:
                raise MeApiException(response.status_code, str(response_text.get('detail') or response_text.get('phone_number') or response_text), response.reason)
            return response_text
        else:
            raise MeException(f"Error when trying to send a {req_type} request to {url}, with body:\n{body} and with headers:\n{headers}.")
