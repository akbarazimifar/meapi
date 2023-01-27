import locale
import logging
from enum import Enum
from json import JSONDecodeError, loads
from os import environ
from re import match
from typing import Union, TYPE_CHECKING, Optional, List, Dict, Any
import meapi
from meapi.api.raw.auth import generate_new_access_token_raw, activate_account_raw, ask_for_sms_raw, ask_for_call_raw
from meapi.api.raw.account import update_profile_details_raw, update_fcm_token_raw, add_contacts_raw, add_calls_raw
from meapi.api.raw.notifications import unread_notifications_count_raw
from meapi.api.raw.settings import get_settings_raw, change_settings_raw
from meapi.api.raw.social import numbers_count_raw, get_news_raw
from meapi.models.others import AuthData, NewAccountDetails
from meapi.utils.exceptions import MeException, MeApiException, MeApiError, BlockedMaxVerifyReached, IncorrectPwdToken, \
    BrokenCredentialsManager, BlockedAccount, NewAccountException, ForbiddenRequest
from meapi.utils.helpers import generate_session_token, ANDROID_VERSION_NAME, ANDROID_VERSION_CODE, HEADERS
from meapi.utils.randomator import get_random_carrier, get_random_country_code, get_random_adv_id, generate_random_data
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

_logger = logging.getLogger(__name__)

ME_BASE_API = 'https://app.mobile.me.app'
WA_AUTH_URL = "https://wa.me/972543229534?text=Connectme"
TG_AUTH_URL = "http://t.me/Meofficialbot?start=__iw__{}"
AUTH_SCHEMA = {key: str for key in ('access', 'refresh', 'pwd_token')}


class AuthMethod(Enum):
    """
    Enum for Auth methods.
    """
    WHATSAPP_OR_TELEGRAM = 1
    SMS = 2
    CALL = 3


class AuthMethods:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise TypeError(
            "Auth class is not intended to create an instance's but only to be inherited by Me class."
        )

    def _login(
            self: 'Me',
            activation_code: Optional[str] = None,
            new_account_details: Optional[NewAccountDetails] = None,
            raise_new_account_exception: bool = False
    ) -> bool:
        """
        Activate new phone number account.
        - If ``activation_code`` is not provided, the method will prompt for activation code via WhatsApp,
        Telegram, SMS or Call.

        :param activation_code: You can pass the activation code if you want to skip the prompt. *Default:* ``None``.
        :type activation_code: ``str`` | ``None``
        :param new_account_details: You can pass the new account details if you want to skip the prompt in case
        of new account. Default: ``None``.
        :type new_account_details: ``NewAccountDetails`` | ``None``
        :param raise_new_account_exception: If ``True``, the method will raise ``NewAccountException``
         instead of prompting for new account details if the phone number is not registered yet and
         ``new_account_details`` not provided. *Default:* ``False``.
        :type raise_new_account_exception: ``bool``
        :raises ValueError: If pre-activation-code is not valid.
        :return: Is login successful.
        :rtype: ``bool``
        """
        need_emulate = False
        if self._auth_data is None and self.phone_number:
            activate_already = False
            while self._auth_data is None:
                credentials = self._credentials_manager.get(str(self.phone_number))
                self._auth_data = AuthData(**credentials) if credentials else None
                if self._auth_data is None:
                    if activate_already:
                        raise BrokenCredentialsManager
                    need_emulate = True  # first time activation

                    if activation_code and not match(r'^\d{6}$', str(activation_code)):
                        raise ValueError("Not a valid 6-digits activation code!")

                    while not activation_code:  # prompt for activation code
                        anti_session_key = environ.get('ANTI_SESSION_BOT_KEY', None)
                        print(f"Welcome to MeApi (version {meapi.__version__}) • Copyright (C) {meapi.__copyright__}\n"
                              f"\t\t\t\t<https://github.com/david-lev/meapi>\n"
                              f"MeApi is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
                              f"\t\t\t\tunder the terms of the {meapi.__license__} License.\n")
                        print(f"* In order to use MeApi, you need to verify your phone number: {self.phone_number}")
                        if not anti_session_key:
                            msg = f"* WhatsApp (Recommended): {WA_AUTH_URL}\n* Telegram: {TG_AUTH_URL.format(self.phone_number)}\n"
                            print(msg)
                        else:
                            print("You need to choose an authorization method:"
                                  "\n# 1: WhatsApp or Telegram\n# 2: SMS\n# 3: Call")
                            method = None
                            while method is None:
                                try:
                                    method = AuthMethod(int(input("* Enter the number of the method: ")))
                                except ValueError:
                                    print("* You need to choose a number between 1 and 3!")
                                    continue
                                err_msg = "* An error occurred in the process." \
                                          "You can only verify at this time using WhatsApp or Telegram."
                                if method == AuthMethod.WHATSAPP_OR_TELEGRAM:
                                    print(f"* WhatsApp (Recommended): {WA_AUTH_URL}\n"
                                          f"* Telegram: {TG_AUTH_URL.format(self.phone_number)}\n")
                                    break
                                elif method == AuthMethod.SMS:
                                    if self._ask_for_sms():
                                        print(f"* Sending SMS to: {self.phone_number}\n")
                                        break
                                    print(err_msg)
                                elif method == AuthMethod.CALL:
                                    if self._ask_for_call():
                                        print(f"* Calling to: {self.phone_number}\n")
                                        break
                                    print(err_msg)

                        activation_code = input("** Enter your verification code (6 digits): ")
                        while not match(r'^\d{6}$', str(activation_code)):
                            activation_code = input("** Incorrect code. The verification code"
                                                    " includes 6 digits. Please enter: ")
                    self._auth_data = AuthData(**activate_account_raw(self, self.phone_number, activation_code))
                    self._credentials_manager.set(str(self.phone_number), self._auth_data.as_dict())

                try:
                    self.uuid = self.get_uuid()
                except MeApiException as e:
                    if e.http_status == 401:
                        if new_account_details is None and raise_new_account_exception:
                            raise NewAccountException(http_status=e.http_status, msg=e.msg)
                        self._register(new_account_details=new_account_details)
                        need_emulate = True
                activate_already = True
        if need_emulate:
            self._emulate_app()
        return True

    def _emulate_app(self: 'Me') -> bool:
        """
        Well, this method basically emulates the app login process by calling some endpoints and updating some data.
        """
        _logger.debug("Emulating app login process...")
        try:
            update_profile_details_raw(
                client=self,
                carrier=get_random_carrier(),
                country_code=get_random_country_code(),
                device_type='android',
                gdpr_consent=True,
                phone_prefix=int(str(self.phone_number)[:3])
            )
        except MeApiException as err:
            if err.http_status == 401 and err.msg == 'User is blocked for patch':
                err = BlockedAccount(err.http_status, err.msg)
            raise err
        change_settings_raw(client=self, language=locale.getdefaultlocale()[0].split('_')[0])
        add_contacts_raw(client=self, contacts=[c.as_dict() for c in generate_random_data(contacts=True).contacts])
        get_news_raw(client=self, os_type='android')
        numbers_count_raw(client=self)
        get_settings_raw(client=self)
        update_profile_details_raw(
            client=self,
            app_version=f'{ANDROID_VERSION_NAME}({ANDROID_VERSION_CODE})',
            model_name='samsung o1s',
            operating_system_version='android : 12 : S : sdk=31'
        )
        unread_notifications_count_raw(client=self)
        add_calls_raw(client=self, calls=[c.as_dict() for c in generate_random_data(calls=True).calls])
        update_fcm_token_raw(self, '')
        update_profile_details_raw(self, adv_id=get_random_adv_id())
        return True

    def _register(self: 'Me', new_account_details: Optional[NewAccountDetails] = None) -> bool:
        """
        Register new account.
            - Internal function to register new account and return the new UUID.

        :param new_account_details: Optional NewAccountDetails object instead of prompting the user.
        :type new_account_details: :py:class:`~meapi.models.others.NewAccountDetails`
        :return: True if the registration was successful.
        :rtype: bool
        """
        if new_account_details is None:
            print("** This is a new account and you need to register first.")
            first_name = None
            last_name = None
            email = ''

            while not first_name:
                first_name = input("* Enter your first name (Required): ")

            while last_name is None:
                last_name = input("* Enter your last name (Optional): ")

            while email == '':
                email = input("* Enter your email (Optional): ") or None

            new_account_details = NewAccountDetails(
                first_name=first_name, last_name=last_name, email=email
            )

        is_success, profile = self.update_profile_details(
            first_name=new_account_details.first_name,
            last_name=new_account_details.last_name,
            email=new_account_details.email,
            login_type='email',
            facebook_url=None,
            google_url=None
        )
        if is_success:
            print("** Your profile successfully created! **\n")
            self.uuid = profile.uuid
            return True
        raise MeException("Can't update the profile. Please check your input again.")

    def _generate_access_token(self: 'Me') -> bool:
        """
        Generate new access token.

        :raises MeApiException: msg: ``api_incorrect_pwd_token`` if ``pwd_token`` is broken.
        In this case, you need to generate a new ``pwd_token``. by calling to :py:func:`~meapi.Me._activate_account`.
        :return: Is success.
        :type: ``bool``
        """
        existing_data = self._credentials_manager.get(str(self.phone_number))
        if existing_data is None:
            if self._login():
                return True
            else:
                raise MeException("Failed to generate access token!")
        try:
            existing_data = AuthData(**existing_data)
        except TypeError:
            raise BrokenCredentialsManager
        try:
            new_auth_data = generate_new_access_token_raw(self, str(self.phone_number), existing_data.pwd_token)
            self._auth_data = AuthData(
                access=new_auth_data['access'], refresh=new_auth_data['refresh'], pwd_token=existing_data.pwd_token
            )
        except MeApiException as err:
            if isinstance(err, IncorrectPwdToken):
                self._credentials_manager.delete(str(self.phone_number))
            raise err
        self._credentials_manager.update(phone_number=str(self.phone_number), access_token=self._auth_data.access)
        return True

    def _ask_for_code(self: 'Me', auth_method: AuthMethod) -> bool:
        """
        Ask me to send a code to the phone number by sms or call.
        """
        try:
            session_token = generate_session_token(environ.get('ANTI_SESSION_BOT_KEY'), self.phone_number)
        except Exception as err:
            print('ERROR: ' + str(err))
            return False
        try:
            if auth_method == AuthMethod.SMS:
                return ask_for_sms_raw(self, str(self.phone_number), session_token)["success"]
            elif auth_method == AuthMethod.CALL:
                return ask_for_call_raw(self, str(self.phone_number), session_token)["success"]
        except MeApiException as err:
            if isinstance(err, BlockedMaxVerifyReached):
                print("You have reached the maximum number of attempts to verify your phone number with sms or call!")
            else:
                print(err)
            return False

    def _ask_for_call(self: 'Me') -> bool:
        """Ask me to send a code to the phone number by call."""
        return self._ask_for_code(AuthMethod.CALL)

    def _ask_for_sms(self: 'Me') -> bool:
        """Ask me to send a code to the phone number by sms."""
        return self._ask_for_code(AuthMethod.SMS)

    def _logout(self: 'Me') -> bool:
        """
        Logout from Me account (And delete credentials, depends on the credentials manager implementation).

        :return: Is success.
        :type: ``bool``
        """
        self._credentials_manager.delete(str(self.phone_number))
        return True

    def _make_request(self: 'Me',
                      req_type: str,
                      endpoint: str,
                      body: Dict[str, Any] = None,
                      headers: Dict[str, Any] = None,
                      files: Dict[str, Any] = None,
                      ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Internal method to make requests to Me api and return the response.

        :param req_type: HTTP request type: ``post``, ``get``, ``put``, ``patch``, ``delete``.
        :type req_type: ``str``
        :param endpoint: api endpoint.
        :type endpoint: ``str``
        :param body: The body of the request. Default: ``None``.
        :type body: ``dict``
        :param headers: Use different headers instead of the default.
        :type headers: ``dict``
        :raises MeApiException: If HTTP status is higher than 400.
        :raises ValueError: If the response received does not contain a valid JSON or the request type is not valid.
        :raises ConnectionError: If the request failed.
        :return: API response as dict or list.
        :rtype:  ``dict`` | ``list``
        """
        url = ME_BASE_API + endpoint
        request_types = ('post', 'get', 'put', 'patch', 'delete')
        if req_type not in request_types:
            raise ValueError("Request type not in requests type list!!\nAvailable types: " + ", ".join(request_types))
        if headers is None:
            headers = HEADERS
        max_rounds = 3
        while max_rounds > 0:
            max_rounds -= 1
            if self._auth_data:
                headers['authorization'] = self._auth_data.access
            _logger.debug(f"Making {req_type} request to {url} with body: {body} and headers: {headers}")
            response = getattr(self._session, req_type)(url=url, json=body, files=files, headers=headers)
            try:
                response_text = loads(response.text)
            except JSONDecodeError:
                raise ValueError(f"The response (Status code: {response.status_code}) "
                                 f"received does not contain a valid JSON:\n" + str(response.text))
            if response.status_code == 403:
                if self.phone_number:
                    if self._generate_access_token():
                        continue
                else:  # official authentication method, no pwd_token to generate access token
                    raise ForbiddenRequest(http_status=response.status_code, msg=str(response_text.get('detail')))

            if response.status_code >= 400:
                try:
                    if isinstance(response_text, dict):
                        msg = response_text.get('detail') or response_text.get('phone_number') or \
                              list(response_text.values())[0][0]
                    elif isinstance(response_text, list):
                        msg = response_text[0]
                    else:
                        msg = response_text
                except (IndexError, KeyError):
                    msg = response_text
                MeApiError.raise_exception(response.status_code, str(msg))
            return response_text
        else:
            raise ConnectionError(
                f"Error when trying to send a {req_type} request to {url}, "
                f"with body:\n{body} and with headers:\n{headers}.")

