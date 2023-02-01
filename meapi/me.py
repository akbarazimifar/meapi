import os
import requests
import logging
from typing import Union, Optional, Any
import meapi
from meapi.models.me_model import MeModel
from meapi.models.others import NewAccountDetails, AuthData
from meapi.api.client.account import AccountMethods
from meapi.api.client.notifications import NotificationsMethods
from meapi.api.client.settings import SettingsMethods
from meapi.api.client.social import SocialMethods
from meapi.api.client.auth import AuthMethods
from meapi.utils.exceptions import FrozenInstance, NotValidPhoneNumber, NotValidAccessToken
from meapi.utils.helpers import logo
from meapi.utils.validators import validate_phone_number, validate_access_token
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
        - Source code: `GitHub <https://github.com/david-lev/meapi>`_
        - See `Setup <https://meapi.readthedocs.io/en/latest/content/setup.html>`_ to get started.
        - See `Client <https://meapi.readthedocs.io/en/latest/content/client.html>`_ for all the available methods.

    Examples to setting up the client:

        >>> from meapi import Me
        >>> me = Me(phone_number=972123456789) # Unofficial method, phone number is required, activation code will be prompted.
        >>> me = Me(phone_number=972123456789, activation_code='123456') # Unofficial method with pre-provided activation code.
        >>> me = Me(access_token='xxxxxxxxxxxx') # Official method, access token is required (saved in memory).
        >>> me = Me(phone_number=972123456789, credentials_manager=RedisCredentialsManager(redis_con)) # With custom credentials manager.
        >>> me = Me(phone_number=972123456789, interactive_mode=True) # With interactive mode (prompt for missing data instead of raising exceptions).
        >>> me = Me(phone_number=972123456789, activation_code='123456', new_account_details=NewAccountDetails(first_name='Chandler', last_name='Bing')) # New account registration.

    :param interactive_mode: If ``True``, the client will prompt for missing data instead of raising exceptions (See `Interactive mode <https://meapi.readthedocs.io/en/latest/content/setup.html#the-interactive-way>`_). *Default:* ``False``.
    :type interactive_mode: ``bool``
    :param phone_number: International phone number format (Required on the `Unofficial method <https://meapi.readthedocs.io/en/latest/content/setup.html#unofficial-method>`_). *Default:* ``None``.
    :type phone_number: ``str`` | ``int`` | ``None``
    :param access_token: Official access token (Required on the `Official method <https://meapi.readthedocs.io/en/latest/content/setup.html#official-method>`_). *Default:* ``None``
    :type access_token: ``str`` | ``None``
    :param activation_code: Activation code (``NeedActivationCode`` exception will be raised if not provided and ``interactive_mode`` is ``False``). *Default:* ``None``
    :type activation_code: ``str`` | ``None``
    :param credentials_manager: Credentials manager to use in order to store and manage the credentials (See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_). *Default:* :py:obj:`~meapi.credentials_managers.json.JsonCredentialsManager`.
    :type credentials_manager: :py:obj:`~meapi.credentials_managers.CredentialsManager` | ``None``
    :param new_account_details: Account details for new account registration without the need for a prompt (even if ``interactive_mode`` is ``True``). *Default:* ``None``.
    :type new_account_details: :py:obj:`~meapi.models.others.NewAccountDetails` | ``None``
    :param session: requests Session object. Default: ``None``.
    :type session: ``requests.Session`` | ``None``

    :raises NotValidPhoneNumber: If ``phone_number`` is not valid.
    :raises NotValidAccessToken: If ``access_token`` is not valid.
    :raises NeedActivationCode: If the account is not activated and ``activation_code`` is not provided and ``interactive_mode`` is ``False``.
    :raises IncorrectActivationCode: If the ``activation_code`` is incorrect and ``interactive_mode`` is ``False``.
    :raises ActivationCodeExpired: If the ``activation_code`` is correct but expired (Request a new one) and ``interactive_mode`` is ``False``.
    :raises MaxValidateReached: If the ``activation_code`` is not correct and the max number of tries reached (Request a new one).
    :raises ValueError: If both ``phone_number`` and ``access_token`` are provided.
    :raises NewAccountException: If this is new account and ``new_account_details`` is not provided and ``interactive_mode`` is ``False``.
    :raises TypeError: If ``credentials_manager`` is not an instance of :py:obj:`~meapi.credentials_managers.CredentialsManager`.
    :raises BlockedAccount: If the account is blocked (You need to contact Me support).
    :raises IncorrectPwdToken: If the ``pwd_token`` provided by the credentials manager is broken (You need to re-login).
    :raises PhoneNumberDoesntExists: If the ``phone_number`` does not exist (Probably not valid phone number).
    :raises BrokenCredentialsManager: If the ``credentials_manager`` not providing the expected data.
    :raises ForbiddenRequest: In the official method, if the ``access_token`` is not valid.
    :raises FrozenInstance: If you try to change the value of an attribute.
    """
    def __init__(self,
                 phone_number: Union[int, str] = None,
                 access_token: Optional[str] = None,
                 activation_code: Optional[str] = None,
                 credentials_manager: Optional[CredentialsManager] = None,
                 new_account_details: Optional[NewAccountDetails] = None,
                 interactive_mode: bool = False,
                 session: Optional[requests.Session] = None
                 ):
        # check for the presence of the phone number or access token
        if not access_token and not phone_number:
            access_token = self._choose_login_method(access_token=access_token, interactive_mode=interactive_mode)
        elif access_token and phone_number:
            raise ValueError("You can't provide both phone number and access token!")
        elif access_token and not phone_number:
            access_token = validate_access_token(access_token)
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
        self._interactive_mode = interactive_mode
        self._session = session or requests.Session()  # create new session if not provided
        self._auth_data = None if not access_token else AuthData(access=access_token, refresh=access_token)
        self.login(
            activation_code=activation_code, new_account_details=new_account_details, interactive_mode=interactive_mode
        )

    def _choose_login_method(self, access_token, interactive_mode):
        if interactive_mode:
            print(logo.format(version=meapi.__version__, copyright=meapi.__copyright__, license=meapi.__license__))
            print("How do you want to login?\n"
                  "\t1. Unofficial method (phone number)\n\t2. Official method (access token)\n")
            while True:
                try:
                    choice = int(input("Please enter your choice: "))
                    if choice not in (1, 2):
                        print("Please enter a valid choice!")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid choice!")
            while True:
                if choice == 1:
                    try:
                        self.phone_number = validate_phone_number(input("Please enter your phone number: "))
                        break
                    except NotValidPhoneNumber:
                        print("Please enter a valid phone number!")
                elif choice == 2:
                    try:
                        access_token = validate_access_token(input("Please enter your access token: "))
                        self.phone_number = None
                        break
                    except NotValidAccessToken:
                        print("Please enter a valid access token!")
        else:
            raise ValueError("You need to provide phone number or access token!")
        return access_token

    def __setattr__(self, key: str, value: Any):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_Me__init_done', None):
            if key in ('phone_number', 'uuid', '_credentials_manager', '_interactive_mode', '_session', '_auth_data'):
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)
