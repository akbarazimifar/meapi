from json import JSONDecodeError, loads
from os import environ
from re import match
from time import sleep
from typing import Union, TYPE_CHECKING
from meapi.api.raw.auth import generate_new_access_token_raw, activate_account_raw, ask_for_sms_raw, ask_for_call_raw
from meapi.utils.exceptions import MeException, MeApiException
from meapi.utils.helpers import _get_session, HEADERS
from meapi.utils.validations import validate_auth_response

if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

ME_BASE_API = 'https://app.mobile.me.app'
wa_auth_url = "https://wa.me/972543229534?text=Connectme"
tg_auth_url = "http://t.me/Meofficialbot?start=__iw__{}"


class Auth:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise MeException("Auth class is not intended to create an instance's but only to be inherited by Me class.")

    def _activate_account(self: 'Me', activation_code: str = None) -> bool:
        """
        Activate new phone number account.
        - If ``activation_code`` is not provided, the method will prompt for activation code via WhatsApp, Telegram, SMS or Call.

        :param activation_code: You can pass the activation code if you want to skip the prompt. *Default:* ``None``.
        :type activation_code: ``str`` | ``None``
        :raises MeException: If pre-activation-code is not valid.
        :raises MeApiException:
            - **msg's:**
            - ``api_phone_number_doesnt_exists`` if not a valid ``phone_number``.
            - ``api_activation_code_expired``, ``api_incorrect_activation_code`` If activation-code is incorrect.
        :return: Is success.
        :rtype: ``bool``
        """
        if not activation_code and self._activation_code:
            activation_code = self._activation_code
            self._activation_code = None  # expire after one use

        if activation_code and not match(r'^\d{6}$', str(activation_code)):
            raise MeException("Not a valid 6-digits activation code!")
        if not activation_code:
            methods = {1: 'wa_tg', 2: 'sms', 3: 'call'}
            anti_session_key = environ.get('ANTI_SESSION_BOT_KEY', None)
            print("To get access token you need to authorize yourself:\n")
            if not anti_session_key:
                msg = f"* WhatsApp (Recommended): {wa_auth_url}\n* Telegram: {tg_auth_url.format(self.phone_number)}\n"
                print(msg)
            else:
                print("You need to choose an authorization method:\n# 1: WhatsApp or Telegram\n# 2: SMS\n# 3: Call")
                method = None
                while not method:
                    try:
                        method = methods[int(input("* Enter the number of the method: "))]
                    except (ValueError, KeyError):
                        print("* You need to choose a number between 1 and 3!")
                        sleep(1)
                        method = None
                        continue
                    err_msg = "* An error occurred in the process." \
                              "You can only verify at this time using WhatsApp or Telegram."
                    if method == methods[1]:
                        print(
                            f"* WhatsApp (Recommended): {wa_auth_url}\n* Telegram: {tg_auth_url.format(self.phone_number)}\n")
                        break
                    elif method == methods[2]:
                        if self._ask_for_sms():
                            print(f"* Sending SMS to: {self.phone_number}\n")
                            break
                        print(err_msg)
                        method = methods[1]
                    elif method == methods[3]:
                        if self._ask_for_call():
                            print(f"* Calling to: {self.phone_number}\n")
                            break
                        print(err_msg)
                        method = methods[1]

        while not activation_code:
            activation_code = input("** Enter your verification code (6 digits): ")
            while not match(r'^\d{6}$', str(activation_code)):
                activation_code = input("** Incorrect code. The verification code includes 6 digits. Please enter: ")
        try:
            results = activate_account_raw(self, self.phone_number, activation_code)
            if results.get('access'):
                access_token = results['access']
            else:
                raise MeException(str(results))
        except MeApiException as err:
            if err.http_status == 400 and err.msg == 'api_incorrect_activation_code':
                err.reason = "Wrong activation code!"
            elif err.http_status == 400 and err.msg == 'api_phone_number_doesnt_exists':
                err.reason = "Not a valid phone number!"
            raise err

        if access_token:
            self._access_token = access_token  # in order to get the uuid.
            self.uuid = results['uuid'] = self.get_uuid()  # if this is a new account, you will need to create one.
            self._credentials_manager.set(str(self.phone_number), validate_auth_response(results))
            return True
        return False

    def _ask_for_code(self: 'Me', code_method: str):
        try:
            session_token = _get_session(environ.get('ANTI_SESSION_BOT_KEY'), self.phone_number)
        except Exception as err:
            print('ERROR: ' + str(err))
            return False
        try:
            if code_method == "sms":
                return ask_for_sms_raw(self, str(self.phone_number), session_token)
            elif code_method == "call":
                return ask_for_call_raw(self, str(self.phone_number), session_token)
        except MeApiException as err:
            if err.http_status == 400 and err.msg == 'api_blocked_max_verify_reached':
                print("You have reached the maximum number of attempts to verify your phone number with sms or call!")
            else:
                print(err)
            return False

    def _ask_for_call(self: 'Me'):
        return self._ask_for_code("call")

    def _ask_for_sms(self: 'Me'):
        return self._ask_for_code("sms")

    def _generate_access_token(self: 'Me') -> bool:
        """
        Generate new access token.

        :raises MeApiException: msg: ``api_incorrect_pwd_token`` if ``pwd_token`` is broken.
        In this case, you need to generate a new ``pwd_token``. by calling to :py:func:`~meapi.Me._activate_account`.
        :return: Is success.
        :type: ``bool``
        """
        existing_data = validate_auth_response(self._credentials_manager.get(str(self.phone_number)))
        if not existing_data:
            if self._activate_account():
                return True
            else:
                raise MeException("Failed to generate access token!")
        try:
            auth_data = generate_new_access_token_raw(self, str(self.phone_number), existing_data['pwd_token'])
        except MeApiException as err:
            if err.http_status == 400 and err.msg == 'api_incorrect_pwd_token':
                err.reason = f"Your 'pwd_token' in is broken (You probably activated the account elsewhere)." \
                             f"You need to call 'client._activate_account()' or create new instance of Me() in "\
                             "order to generate a new 'pwd_token'."
                self._credentials_manager.delete(str(self.phone_number))
            raise err
        if auth_data.get('access'):
            self._credentials_manager.update(phone_number=str(self.phone_number), access_token=auth_data['access'])
            return True
        return False

    def _logout(self: 'Me'):
        self._credentials_manager.delete(str(self.phone_number))

    def _make_request(self: 'Me',
                      req_type: str,
                      endpoint: str,
                      body: dict = None,
                      headers: dict = None,
                      files: dict = None,
                      ) -> Union[dict, list]:
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
        :raises MeApiException: If HTTP status is bigger than ``400``.
        :return: API response as dict or list.
        :rtype:  ``dict`` | ``list``
        """
        url = ME_BASE_API + endpoint
        request_types = ['post', 'get', 'put', 'patch', 'delete']
        if req_type not in request_types:
            raise MeException("Request type not in requests type list!!\nAvailable types: " + ", ".join(request_types))
        if headers is None:
            headers = HEADERS
        max_rounds = 3
        while max_rounds != 0:
            max_rounds -= 1
            headers['authorization'] = self._access_token
            response = getattr(self._session, req_type)(url=url, json=body, files=files, headers=headers, proxies=self._proxies)
            try:
                response_text = loads(response.text)
            except JSONDecodeError:
                raise MeException(f"The response (Status code: {response.status_code}) received does not contain a valid JSON:\n" + str(response.text))
            if response.status_code == 403 and self.phone_number:
                if self._generate_access_token():
                    self._access_token = validate_auth_response(self._credentials_manager.get(str(self.phone_number))).get('access')
                    continue
                raise MeException("Cannot generate new access token!")

            if response.status_code >= 400:
                try:
                    if isinstance(response_text, dict):
                        msg = response_text.get('detail') or response_text.get('phone_number') or list(response_text.values())[0][0]
                    elif isinstance(response_text, list):
                        msg = response_text[0]
                    else:
                        msg = response_text
                except:
                    msg = response_text
                raise MeApiException(http_status=response.status_code, msg=str(msg), reason=response.reason)
            return response_text
        else:
            raise MeException(f"Error when trying to send a {req_type} request to {url}, with body:\n{body} and with headers:\n{headers}.")
