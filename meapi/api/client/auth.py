import locale
import logging
import os
import re
import meapi
from json import JSONDecodeError, loads
from typing import Union, TYPE_CHECKING, Optional, List, Dict, Any
from meapi.api.raw.auth import generate_new_access_token_raw, activate_account_raw, ask_for_sms_raw, ask_for_call_raw
from meapi.api.raw.account import update_profile_details_raw, update_fcm_token_raw, add_contacts_raw, add_calls_raw
from meapi.api.raw.notifications import unread_notifications_count_raw
from meapi.api.raw.settings import get_settings_raw, change_settings_raw
from meapi.api.raw.social import numbers_count_raw, get_news_raw
from meapi.models.others import AuthData, NewAccountDetails, RequestType, AuthMethod
from meapi.utils.exceptions import MeException, MeApiException, MeApiError, BlockedMaxVerifyReached, IncorrectPwdToken, \
    BrokenCredentialsManager, BlockedAccount, NewAccountException, ForbiddenRequest, NeedActivationCode, \
    IncorrectActivationCode, ActivationCodeExpired, PhoneNumberDoesntExists, NotLoggedIn
from meapi.utils.helpers import generate_session_token, AVN, AVC, HEADERS
from meapi.utils.randomator import get_random_carrier, get_random_country_code, get_random_adv_id, generate_random_data
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

_logger = logging.getLogger(__name__)

ME_BASE_API = 'https://app.mobile.me.app'
WA_AUTH_URL = "https://wa.me/972543229534?text=Connectme"
TG_AUTH_URL = "http://t.me/Meofficialbot?start=__iw__{}"
AUTH_SCHEMA = {key: str for key in ('access', 'refresh', 'pwd_token')}


class AuthMethods:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise TypeError(
            "Auth class is not intended to create an instance's but only to be inherited by Me class."
        )

    def login(
            self: 'Me',
            activation_code: Optional[str] = None,
            new_account_details: Optional[NewAccountDetails] = None,
            interactive_mode: bool = False
    ) -> bool:
        """
        Login to MeApi.

            - If you initialized the ``Me`` class directly, this method will be called automatically. No need to call it.
            - If ``activation_code`` is not provided and ``interactive_mode`` is ``True`` the method will prompt for activation code.
            - If the account is new and ``new_account_details`` is not provided and ``interactive_mode`` is ``True`` the method will prompt for new account details.

        :param activation_code: You can pass the activation code if you want to skip the prompt. *Default:* ``None``.
        :type activation_code: ``str`` | ``None``
        :param new_account_details: You can pass the new account details if you want to skip the prompt in case of new account. Default: ``None``.
        :type new_account_details: ``NewAccountDetails`` | ``None``
        :param interactive_mode: If ``True`` the method will prompt for activation code (and new account details in case of new account). *Default:* ``False``.
        :type interactive_mode: ``bool``
        :raises NeedActivationCode: If ``activation_code`` is not provided and ``interactive_mode`` is ``False``.
        :raises IncorrectActivationCode: If the activation code is incorrect and ``interactive_mode`` is ``False``.
        :raises ActivationCodeExpired: If the activation code is expired and ``interactive_mode`` is ``False``.
        :raises MaxValidateReached: If ``activation_code`` is incorrect for a few times.
        :raises NewAccountException: If the account is new and ``new_account_details`` is not provided and ``interactive_mode`` is ``False``.
        :raises BrokenCredentialsManager: If the credentials manager is broken (if authentication succeeded but the credentials manager failed to save the credentials).

        :return: Is login succeeded.
        :rtype: ``bool``
        """
        if self._auth_data is None and self.phone_number:
            self._Me__init_done = False
            interactive_mode = interactive_mode or self._interactive_mode
            if not interactive_mode and activation_code is None:
                raise NeedActivationCode
            need_emulate = False
            activate_already = False
            while self._auth_data is None:
                try:
                    credentials = self._credentials_manager.get(phone_number=str(self.phone_number))
                except TypeError as e:
                    raise BrokenCredentialsManager(str(e))
                self._auth_data = AuthData(**credentials) if credentials else None
                if self._auth_data is None:
                    if activate_already:
                        raise BrokenCredentialsManager
                    need_emulate = True  # first time activation
                    self._activate(activation_code, interactive_mode)
                try:
                    self.uuid = self.get_uuid()
                except MeApiException as e:
                    if e.http_status == 401:
                        if new_account_details is None and not interactive_mode:
                            raise NewAccountException(http_status=e.http_status, msg=e.msg)
                        self._register(new_account_details=new_account_details)
                        need_emulate = True
                activate_already = True
            if need_emulate:
                self._emulate_app()
        self._Me__init_done = True
        if interactive_mode:
            print("You are now logged in!")
        return True

    def logout(self: 'Me') -> bool:
        """
        Logout from Me account (And delete credentials, depends on the credentials manager implementation).
            - If you want to login again, you need to call :py:func:`login` or create a new instance of :py:obj:`~meapi.me.Me`.
            - If you try to use any method that requires authentication, you will get a :py:obj:`~meapi.utils.exceptions.NotLoggedIn` exception.

        :return: Is success.
        :type: ``bool``
        """
        try:
            self._credentials_manager.delete(phone_number=str(self.phone_number))
        except TypeError as e:
            raise BrokenCredentialsManager(str(e))
        self._Me__init_done = False
        self._auth_data = None
        return True

    def _activate(self: 'Me', activation_code: Optional[str], interactive_mode: bool):
        if activation_code is None:
            if interactive_mode:
                self._choose_verification()
                while activation_code is None:
                    activation_code = input("Enter the activation code you received (6 digits): ")
                    if not re.match(r'^\d{6}$', str(activation_code)):
                        print("Not a valid 6-digits activation code!")
                        activation_code = None
                        continue
            else:
                raise NeedActivationCode
        if interactive_mode:
            while True:
                try:
                    self._auth_data = AuthData(**activate_account_raw(
                        client=self, phone_number=self.phone_number, activation_code=activation_code
                    ))
                    break
                except (IncorrectActivationCode, ActivationCodeExpired, PhoneNumberDoesntExists) as e:
                    print(e.reason)
                    activation_code = input("Enter the activation code you received (6 digits): ")
                    continue
        else:
            if not re.match(r'^\d{6}$', str(activation_code)):
                raise IncorrectActivationCode(
                    http_status=400,
                    msg=MeApiError.INCORRECT_ACTIVATION_CODE.name.lower(),
                    reason="Not a valid 6-digits activation code!"
                )
            self._auth_data = AuthData(**activate_account_raw(
                client=self, phone_number=self.phone_number, activation_code=activation_code
            ))
        try:
            self._credentials_manager.set(
                phone_number=str(self.phone_number), data=self._auth_data.as_dict()
            )
        except TypeError as e:
            raise BrokenCredentialsManager(str(e))

    def _choose_verification(self: 'Me'):
        anti_session_key = os.environ.get('ANTI_SESSION_BOT_KEY', None)
        print(f"In order to use meapi, you need to verify your phone number in "
              f"one of the following ways:")
        if not anti_session_key:
            msg = f"\t1. WhatsApp (Recommended): {WA_AUTH_URL}\n" \
                  f"\t2. Telegram: {TG_AUTH_URL.format(self.phone_number)}\n"
            print(msg)
        else:
            print("anti_session_key is set, you can use the following link to verify your "
                  "phone number:\n#\t1: WhatsApp or Telegram\n\t2: SMS\n\t3: Call")
            method = None
            while method is None:
                try:
                    method = AuthMethod(int(input("Enter the number of the method: ")))
                except ValueError:
                    print("You need to choose a number between 1 and 3!")
                    continue
                err_msg = "An error occurred in the process." \
                          "You can only verify at this time using WhatsApp or Telegram."
                if method == AuthMethod.WHATSAPP_OR_TELEGRAM:
                    print(f"\tWhatsApp (Recommended): {WA_AUTH_URL}\n"
                          f"\tTelegram: {TG_AUTH_URL.format(self.phone_number)}\n")
                    break
                elif method == AuthMethod.SMS:
                    if self._ask_for_sms():
                        print(f"Sending SMS to: {self.phone_number}...\n")
                        break
                    print(err_msg)
                elif method == AuthMethod.CALL:
                    if self._ask_for_call():
                        print(f"Calling to: {self.phone_number}...\n")
                        break
                    print(err_msg)

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
            print("This is a new account and you need to register first.")
            first_name = None
            last_name = None
            email = ''

            while not first_name:
                first_name = input("Enter your first name (Required): ")

            while last_name is None:
                last_name = input("Enter your last name (Optional): ")

            while email == '':
                email = input("Enter your email (Optional): ") or None

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
            if self._interactive_mode:
                print("Your profile successfully created!")
            self.uuid = profile.uuid
            return True
        raise MeException("Can't update the profile. Please check your input again.")

    def _generate_access_token(self: 'Me') -> bool:
        """
        Generate new access token.

        :raises NotLoggedIn: If the user is not logged in.
        :raises IncorrectPwdToken: If the ``pwd_token`` is incorrect.
        :raises BrokenCredentialsManager: If the credentials manager is broken.
        :return: Is success to generate new access token.
        :type: ``bool``
        """
        if self._auth_data is None:
            raise NotLoggedIn
        try:
            new_auth_data = generate_new_access_token_raw(
                client=self,
                phone_number=str(self.phone_number),
                pwd_token=self._auth_data.pwd_token
            )
            self._auth_data = AuthData(
                pwd_token=self._auth_data.pwd_token,
                **new_auth_data
            )
        except IncorrectPwdToken as err:
            self.logout()
            if self._interactive_mode:
                print(err.reason)
                if self.login(interactive_mode=True):
                    return True
            raise err
        try:
            self._credentials_manager.update(phone_number=str(self.phone_number), access_token=self._auth_data.access)
        except TypeError as e:
            raise BrokenCredentialsManager(str(e))
        return True

    def _ask_for_code(self: 'Me', auth_method: AuthMethod) -> bool:
        """
        Ask me to send a code to the phone number by sms or call.
        """
        try:
            session_token = generate_session_token(os.environ.get('ANTI_SESSION_BOT_KEY'), self.phone_number)
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

    def _emulate_app(self: 'Me') -> bool:
        """
        Well, this method basically emulates the app login process by calling some endpoints and updating some data.
        """
        if self._interactive_mode:
            print("Emulating app login process (this may take a while)...")
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
            app_version=f'{AVN}({AVC})',
            model_name='samsung o1s',
            operating_system_version='android : 12 : S : sdk=31'
        )
        unread_notifications_count_raw(client=self)
        add_calls_raw(client=self, calls=[c.as_dict() for c in generate_random_data(calls=True).calls])
        update_fcm_token_raw(self, '')
        update_profile_details_raw(self, adv_id=get_random_adv_id())
        return True

    def make_request(
            self: 'Me',
            method: Union[str, RequestType],
            endpoint: str,
            body: Dict[str, Any] = None,
            headers: Dict[str, Union[str, int]] = None,
            files: Dict[str, bytes] = None,
      ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Make a request to the API.

        :param method: Request method. Can be ``GET``, ``POST``, ``PUT``, ``DELETE`` or ``PATCH``.
        :type method: ``str`` | :py:class:`~meapi.RequestType`
        :param endpoint: API endpoint. e.g. ``/main/users/profile/me/``.
        :type endpoint: ``str``
        :param body: The body of the request. Default: ``None``.
        :type body: ``dict``
        :param headers: Use different headers instead of the default ones. Default: ``None``.
        :type headers: ``dict``
        :param files: Files to send with the request. Default: ``None``.
        :type files: ``dict``
        :raises MeApiException: If HTTP status is higher than 400.
        :raises ValueError: If the response received does not contain a valid JSON or the request type is not valid.
        :raises ConnectionError: If the request failed.
        :return: API response as dict or list.
        :rtype:  ``dict`` | ``list``
        """
        url = ME_BASE_API + endpoint
        if isinstance(method, RequestType):
            method = method.name
        else:
            method = method.upper()
        request_types = (rt.name for rt in RequestType)
        if method not in request_types:
            raise ValueError("Request type not in requests type list!!\nAvailable types: " + ", ".join(request_types))
        if headers is None:
            headers = HEADERS.copy()
            if self._auth_data is not None:
                headers['authorization'] = self._auth_data.access
        max_rounds = 3
        while max_rounds > 0:
            max_rounds -= 1
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                files=files,
                headers=headers
            )
            try:
                response_text = loads(response.text)
            except JSONDecodeError:
                raise ValueError(f"The response (Status code: {response.status_code}) "
                                 f"received does not contain a valid JSON:\n" + str(response.text))
            if response.status_code == 403:
                if self.phone_number:  # unofficial auth
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
                f"Error when trying to send a {method} request to {url}, "
                f"with body:\n{body} and with headers:\n{headers}.")

