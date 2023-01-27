import os
import re
import requests
import logging
from typing import Union, Optional, Any
from meapi.models.me_model import MeModel
from meapi.models.others import NewAccountDetails, AuthData
from meapi.api.client.account import AccountMethods
from meapi.api.client.notifications import NotificationsMethods
from meapi.api.client.settings import SettingsMethods
from meapi.api.client.social import SocialMethods
from meapi.api.client.auth import AuthMethods
from meapi.utils.exceptions import FrozenInstance
from meapi.utils.validators import validate_phone_number
from meapi.credentials_managers import CredentialsManager
from meapi.credentials_managers.json_files import JsonCredentialsManager
from meapi.credentials_managers.redis import RedisCredentialsManager

if os.environ.get("ENV") == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

_logger = logging.getLogger(__name__)


class Me(MeModel, AuthMethods, AccountMethods, SocialMethods, SettingsMethods, NotificationsMethods):
    """
    The ``Me`` Client. Used to interact with MeAPI.
        - See `Authentication <https://meapi.readthedocs.io/en/latest/content/setup.html#authentication>`_ for more information.

    Examples to setting up the client:

        >>> from meapi import Me
        >>> me = Me(phone_number=972123456789) # Unofficial method, phone number is required, activation code will be prompted.
        >>> me = Me(phone_number=972123456789, activation_code='123456') # Unofficial method with pre-provided activation code.
        >>> me = Me(access_token='xxxxxxxxxxxx') # Official method, access token is required (saved in memory).
        >>> me = Me(phone_number=972123456789, credentials_manager=RedisCredentialsManager(redis_con)) # With custom credentials manager.
        >>> me = Me(phone_number=972123456789, session=requests.Session()) # With custom requests Session.
        >>> me = Me(phone_number=972123456789, new_account_details=NewAccountDetails(first_name='Chandler', last_name='Bing')) # New account registration.


    :param phone_number: International phone number format. *Default:* ``None``.

        - Required on the `Unofficial method <https://meapi.readthedocs.io/en/latest/content/setup.html#unofficial-method>`_.
    :type phone_number: ``str`` | ``int`` | ``None``
    :param activation_code: You can provide pre ``activation_code`` from Me in advance, without the need for a prompt. *Default:* ``None``.
    :type activation_code: ``str`` | ``None``
    :param access_token: Official access token. *Default:* ``None``.

        - Required on the `Official method <https://meapi.readthedocs.io/en/latest/content/setup.html#official-method>`_
    :type access_token: ``str`` | ``None``
    :param credentials_manager: Credentials manager to use in order to store and manage the credentials. *Default:* :py:obj:`~meapi.credentials_managers.json.JsonCredentialsManager`.

        - In the default case, the credentials will be stored in a file named ``meapi_credentials.json`` in the current working directory.
        - See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_.
    :type credentials_manager: :py:obj:`~meapi.credentials_managers.CredentialsManager` | ``None``
    :param new_account_details: Account details for new account registration. *Default:* ``None``.

        - Designed for cases of new account registration without the need for a prompt.
    :type new_account_details: :py:obj:`~meapi.models.others.NewAccountDetails` | ``None``
    :param session: requests Session object. Default: ``None``.
    :type session: ``requests.Session`` | ``None``
    :param raise_new_account_exception: Raise ``NewAccountException`` if this is new account and ``new_account_details`` is not provided. *Default:* ``False``.

        - Designed for cases of new account to catch the exception and handle it.
    :type raise_new_account_exception: ``bool``

    :raises NotValidPhoneNumber: If the ``phone_number`` is not valid.
    :raises ValueError: If both ``phone_number`` and ``access_token`` are not provided or if ``activation_code`` is not valid (6-digits).
    :raises NewAccountException: If this is new account and ``new_account_details`` is not provided and ``raise_new_account_exception`` is ``True``.
    :raises TypeError: If ``credentials_manager`` is not an instance of :py:obj:`~meapi.credentials_managers.CredentialsManager`.
    :raises BlockedAccount: If the account is blocked (You need to contact Me support).
    :raises IncorrectPwdToken: If the ``pwd_token`` provided by the credentials manager is broken (You need to re-login).
    :raises PhoneNumberDoesntExists: If the ``phone_number`` does not exists (Probably not valid phone number).
    :raises IncorrectActivationCode: If the ``activation_code`` is incorrect.
    :raises ActivationCodeExpired: If the ``activation_code`` is correct but expired (Request a new one).
    :raises BlockedMaxVerifyReached: If the ``phone_number`` reached the maximum number of call or sms verification attempts (you can still verify by WhatsApp or Telegram).
    :raises BrokenCredentialsManager: If the ``credentials_manager`` not providing the expected data.
    :raises ForbiddenRequest: In the official method, if the ``access_token`` is not valid.
    :raises FrozenInstance: If you try to change the value of an attribute.
    """
    def __init__(self,
                 phone_number: Union[int, str] = None,
                 activation_code: Optional[str] = None,
                 access_token: Optional[str] = None,
                 credentials_manager: Optional[CredentialsManager] = None,
                 new_account_details: Optional[NewAccountDetails] = None,
                 raise_new_account_exception: bool = False,
                 session: Optional[requests.Session] = None
                 ):
        # validate pre-activation-code
        if activation_code is not None and not re.match(r'^\d{6}$', str(activation_code)):
            raise ValueError("Not a valid 6-digits activation code!")

        # check for the presence of the phone number or access token
        if not access_token and not phone_number:
            raise ValueError("You need to provide phone number or access token!")
        elif access_token and phone_number:
            raise ValueError("You can't provide both phone number and access token!")
        elif access_token and not phone_number:
            self.phone_number = None
        elif phone_number and not access_token:
            self.phone_number = validate_phone_number(phone_number)

        # check for the presence valid credentials manager, else use default (JsonCredentialsManager)
        if credentials_manager is None:
            self._credentials_manager = JsonCredentialsManager()
        elif isinstance(credentials_manager, CredentialsManager):
            self._credentials_manager = credentials_manager
        else:
            raise TypeError("credentials_manager must be an instance of CredentialsManager!")

        # set the rest of the attributes
        self.uuid = None
        self._session = session or requests.Session()  # create new session if not provided
        self._auth_data = None if not access_token else AuthData(access=access_token, refresh=access_token)
        self._login(
            activation_code=activation_code,
            new_account_details=new_account_details,
            raise_new_account_exception=raise_new_account_exception
        )
        super().__init__()

    def __del__(self):
        if isinstance(getattr(self, '_session', None), requests.Session):
            self._session.close()

    def __setattr__(self, key: str, value: Any):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_Me__init_done', None):
            if key in ('phone_number', 'uuid'):
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)
