from re import match
from typing import Union
from requests import Session
from meapi.api.client.account import Account
from meapi.api.client.notifications import Notifications
from meapi.api.client.settings import Settings
from meapi.api.client.social import Social
from meapi.api.client.auth import Auth
from meapi.utils.credentials_managers import CredentialsManager, JsonFileCredentialsManager
from meapi.utils.exceptions import MeException
from meapi.utils.validations import validate_phone_number, validate_auth_response
from logging import getLogger

_logger = getLogger(__name__)


class Me(Auth, Account, Social, Settings, Notifications):
    """
    Create a new instance to interact with MeAPI.
        - **See** `Authentication <https://meapi.readthedocs.io/en/latest/content/setup.html#authentication>`_ **for more information.**

    :param phone_number: International phone number format. *Default:* ``None``.

        - Required on the `Unofficial method <https://meapi.readthedocs.io/en/latest/content/setup.html#unofficial-method>`_.
    :type phone_number: ``str`` | ``int`` | ``None``
    :param activation_code: You can provide the ``activation_code`` from Me in advance, without the need for a prompt. *Default:* ``None``.
    :type activation_code: ``str`` | ``None``
    :param access_token: Official access token. *Default:* ``None``.

        - Required on the `Official method <https://meapi.readthedocs.io/en/latest/content/setup.html#official-method>`_
    :type access_token: ``str`` | ``None``
    :param credentials_manager: Credentials manager to use in order to store and manage the credentials. *Default:* :py:obj:`~meapi.utils.credentials_managers.JsonFileCredentialsManager`.

        - See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_.
    :type credentials_manager: :py:obj:`~meapi.utils.credentials_managers.CredentialsManager` | ``None``
    :param config_file: Path to credentials json file. *Default:* ``config.json``.

        - Only relevant if you leave ``credentials_manager`` as ``None``.
    :param account_details: You can provide all login details can be provided in dict format. *Default:* ``None``.

        - Designed for cases of new account registration without the need for a prompt.
    :type account_details: ``dict`` | ``None``
    :type config_file: ``str`` | ``None``
    :param session: requests Session object. Default: ``None``.
    :type session: ``requests.Session`` | ``None``
    :param proxies: Dict with proxy configuration. Default: ``None``.
    :type proxies: ``dict`` | ``None``

    Example for ``account_details``::

        {
            'phone_number': 972123456789, # Required always
            'activation_code': '123456', # Required only for the first time
            'first_name': 'Regina', # Required for first account registration
            'last_name': 'Phalange', # Optional for first account registration
            'email': 'kenadams@friends.tv', # Optional for first account registration
            'upload_random_data': True, # Recommended for first account registration. Default: True
            'credentials_manager': None, # Optional. Default: JsonFileCredentialsManager('config.json')
            'session': None, # Optional. Default: new requests.Session()
            'proxies': None, # Optional. Default: None
        }
    """
    def __init__(self,
                 phone_number: Union[int, str] = None,
                 activation_code: str = None,
                 access_token: str = None,
                 account_details: dict = None,
                 credentials_manager: CredentialsManager = None,
                 config_file: str = 'config.json',
                 session: Session = None,
                 proxies: dict = None):
        if account_details:
            if not isinstance(account_details, dict):
                raise MeException("Account details must be in dict format")

            if account_details.get('session'):
                session = account_details['session']
            if account_details.get('proxies'):
                proxies = account_details['proxies']
            if account_details.get('credentials_manager'):
                credentials_manager = account_details['credentials_manager']
            if account_details.get('phone_number'):
                phone_number = account_details['phone_number']
            if account_details.get('activation_code'):
                activation_code = account_details['activation_code']

        # validate pre-activation-code
        if activation_code:
            if not match(r'^\d{6}$', str(activation_code)):
                raise MeException("Not a valid 6-digits activation code!")
        self._activation_code = activation_code

        # check for the presence of the phone number or access token
        if not access_token and not phone_number and not account_details:
            raise MeException("You need to provide phone number, account details or access token!")
        if access_token and phone_number:
            _logger.warning("access_token mode does not accept phone number, ignoring it!")
        if account_details and not phone_number:
            raise MeException("You must provide phone number in account details or phone_number separately!")

        # check for the presence valid credentials manager, else use default (JsonFileCredentialsManager)
        if isinstance(credentials_manager, CredentialsManager):
            self._credentials_manager = credentials_manager
        else:
            self._credentials_manager = JsonFileCredentialsManager(config_file)

        # set the rest of the attributes
        self.phone_number = validate_phone_number(phone_number) if (phone_number and not access_token) else phone_number
        self.uuid = None
        self._access_token = access_token
        self._account_details = account_details
        self._proxies = proxies
        self._session: Session = session or Session()  # create new session if not provided

        # if access_token not provided, try to get it from the credentials manager, if not found, activate the account.
        if not self._access_token:
            auth_data = None
            activate_already = False
            while not auth_data:
                auth_data = self._credentials_manager.get(str(self.phone_number))
                if not auth_data:
                    if activate_already:
                        raise MeException("It seems that the CredentialsManager does not provide the necessary data!")
                    if self._activate_account(self._activation_code):
                        activate_already = True
                    else:
                        raise MeException("Failed to activate the account!")

            validate_auth_response(auth_data)
            self._access_token = auth_data['access']
            self.uuid = auth_data['uuid']

        self.__init_done = True

    def __repr__(self):
        return f"<Me {('phone=' + str(self.phone_number) + ' uuid=' + self.uuid) if self.phone_number else 'access_token mode'} >"

    def __str__(self):
        return str(self.phone_number) if self.phone_number else 'access_token mode'

    def __del__(self):
        if isinstance(getattr(self, '_session', None), Session):
            self._session.close()

    def __setattr__(self, key, value):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_Me__init_done', None):
            if key in ['phone_number', 'uuid', '_activation_code', '_account_details']:
                raise MeException(f"You cannot modify this protected attr '{key}'!")
        return super().__setattr__(key, value)
