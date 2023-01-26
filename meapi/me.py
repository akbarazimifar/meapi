from re import match
from typing import Union, Optional
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
from meapi.credentials_managers.json import JsonCredentialsManager
from meapi.credentials_managers.redis import RedisCredentialsManager

_logger = getLogger(__name__)


class Me(MeModel, Auth, Account, Social, Settings, Notifications):
    """
    The ``Me`` Client. Used to interact with MeAPI.
        - See `Authentication <https://meapi.readthedocs.io/en/latest/content/setup.html#authentication>`_ for more information.

    Example for setting up the client:

        >>> from meapi import Me
        >>> me = Me(phone_number=972123456789) # Unofficial method, phone number is required
        >>> me = Me(phone_number=972123456789, activation_code='123456') # Unofficial method with pre-provided activation code
        >>> me = Me(access_token='xxxxxxxxxxxx') # Official method, access token is required
        >>> me = Me(phone_number=972123456789, credentials_manager=RedisCredentialsManager(redis_con)) # With credentials manager
        >>> me = Me(phone_number=972123456789, session=my_custom_session) # With custom session
        >>> me = Me(account_details={'phone_number': 972123456789, 'activation_code': '123456'...}) # New account registration


    :param phone_number: International phone number format. *Default:* ``None``.

        - Required on the `Unofficial method <https://meapi.readthedocs.io/en/latest/content/setup.html#unofficial-method>`_.
    :type phone_number: ``str`` | ``int`` | ``None``
    :param activation_code: You can provide the ``activation_code`` from ``Me`` in advance, without the need for a prompt. *Default:* ``None``.
    :type activation_code: ``str`` | ``None``
    :param access_token: Official access token. *Default:* ``None``.

        - Required on the `Official method <https://meapi.readthedocs.io/en/latest/content/setup.html#official-method>`_
    :type access_token: ``str`` | ``None``
    :param credentials_manager: Credentials manager to use in order to store and manage the credentials. *Default:* :py:obj:`~meapi.credentials_managers.json.JsonFileCredentialsManager`.

        - See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_.
    :type credentials_manager: :py:obj:`~meapi.utils.credentials_managers.CredentialsManager` | ``None``
    :param config_file: Path to credentials json file. *Default:* ``config.json``.

        - Only relevant if you leave ``credentials_manager`` as ``None``.
    :param account_details: You can provide all login details can be provided in dict format. *Default:* ``None``.

        - Designed for cases of new account registration without the need for a prompt.
        - See example below to all available account details.
    :type account_details: ``dict`` | ``None``
    :type config_file: ``str`` | ``None``
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
    :raises FrozenInstance: If you try to change the value of an attribute.
    """
    def __init__(self,
                 phone_number: Union[int, str] = None,
                 activation_code: str = None,
                 access_token: str = None,
                 account_details: dict = None,
                 credentials_manager: CredentialsManager = None,
                 config_file: str = 'config.json',
                 session: Session = None
                 ):
        # Parse account details
        if account_details:
            account_details_schema = {
                'phone_number': Union[int, str],
                'activation_code': Optional[str],
                'first_name': Optional[str],
                'last_name': Optional[str],
                'email': Optional[str],
                'upload_random_data': Optional[bool],
                'credentials_manager': Optional[CredentialsManager],
                'session': Optional[Session]
            }
            validate_schema_types(account_details_schema, account_details)

            if account_details.get('session'):
                session = account_details['session']
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

            validate_schema_types(AUTH_SCHEMA, auth_data, enforce=True)
            self._access_token = auth_data['access']
            self.uuid = auth_data['uuid']

        self.__init_done = True

    def __repr__(self):
        return f"<Me {('phone=' + str(self.phone_number) + ' uuid=' + self.uuid) if self.phone_number else 'access_token mode'}>"

    def __del__(self):
        if isinstance(getattr(self, '_session', None), Session):
            self._session.close()

    def __setattr__(self, key, value):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_Me__init_done', None):
            if key in ('phone_number', 'uuid', '_activation_code', '_new_account_details'):
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)
