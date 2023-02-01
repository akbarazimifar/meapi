from enum import Enum
from typing import Optional, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from meapi.models.me_model import MeModel


class MeApiException(Exception):
    """
    Raise this exception if http status code is bigger than ``400``.
        - Base class for all api exceptions.

    :param http_status: status code of the http request. ``=>400``.
    :type http_status: int
    :param msg: ``api error msg``. for example: ``api_incorrect_activation_code``.
    :type msg: str
    :param reason: Human reason to the error.
    :type reason: str
    """

    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason

    def __str__(self):
        return f'http status: {self.http_status}, msg: {self.msg}, reason: {self.reason}'


class IncorrectPwdToken(MeApiException):
    """Raise this exception when the pwd token is incorrect. Happens when opening the account elsewhere."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or f"Your 'pwd_token' in is broken (You probably activated the account elsewhere)." \
                                f"\nYou need to re-activate the account by calling the `me._client.login(args)`" \
                                f" method or by creating a new instance o the `Me` class." \
                                f"\n- For more info: https://meapi.readthedocs.io/en/latest/setup.html#initialization"


class PhoneNumberDoesntExists(MeApiException):
    """Raise this exception when the phone number doesn't exist in me database."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "Looks like you haven't ask for a verification code yet."


class IncorrectActivationCode(MeApiException):
    """Raise this exception when the activation code is incorrect."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "Incorrect activation code!"


class BlockedMaxVerifyReached(MeApiException):
    """Raise this exception when the max verify attempts via sms or call reached."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "You have reached the maximum number of attempts " \
                                "to verify your phone number with sms or call!\n" \
                                "- For more info: https://meapi.readthedocs.io/en/latest/setup.html#sms-or-call"


class MaxValidateReached(MeApiException):
    """Raise this exception when the max validate attempts via WhatsApp or Telegram reached."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "You have reached the maximum number of attempts " \
                                "to validate your phone number!"


class ActivationCodeExpired(MeApiException):
    """Raise this exception when the activation code is correct but expired."""
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "The activation code is expired, you need to request new one!"


class SearchPassedLimit(MeApiException):
    """
    Raise this exception when the search passed the limit.
    Happens when searching for a phone number too many times.
    The limit in the unofficial authentication method is 350 searches per day.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "You passed the phone searches limit (About 350 per day in the unofficial auth method)."


class ProfileViewPassedLimit(MeApiException):
    """
    Raise this exception when the profile view passed the limit.
    Happens when viewing profiles too many times.
    The limit in the unofficial authentication method is 500 views per day.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "You passed the profile views limit (About 500 per day in the unofficial auth method)."


class UserCommentsDisabled(MeApiException):
    """
    Raise this exception when the user comments are disabled.
    Happens when trying to publish a comment to a user that disabled comments.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This user disabled comments on his profile!"


class UserCommentsPostingIsNotAllowed(MeApiException):
    """
    Raise this exception when the user comments posting is not allowed.
    Happens when trying to publish a comment to a user that blocked you from commenting.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This user blocked you from commenting on his profile!"


class CommentAlreadyApproved(MeApiException):
    """
    Raise this exception when the comment is already approved.
    Happens when trying to approve a comment that is already approved.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This comment is already approved!"


class CommentAlreadyIgnored(MeApiException):
    """
    Raise this exception when the comment is already ignored.
    Happens when trying to ignore a comment that is already ignored.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This comment is already ignored!"


class NewAccountException(MeApiException):
    """
    Raise this exception when the account is new.
    Happens when trying to login to a new account.
    Provide ``NewAccountDetails`` in the ``Me`` constructor to continue.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This is a new account that needs to be registered!\n" \
                                "- For more info: https://meapi.readthedocs.io/en/latest/content/setup.html#id2"


class BlockedAccount(MeApiException):
    """
    Raise this exception when the account is blocked.
    Happens when trying to login to a blocked account.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "This account is blocked!"


class UnfinishedRegistration(MeApiException):
    """
    Raise this exception when the registration is unfinished.
    Happens when trying to login to an account that is not registered.
    Provide ``NewAccountDetails`` in the ``Me`` constructor to continue.
    """
    pass


class ForbiddenRequest(MeApiException):
    """
    Raise this exception when the request is forbidden.
        - Happens in official authentication method when the access token is expired.
    """
    def __init__(self, http_status: int, msg: str, reason: Optional[str] = None):
        self.http_status = http_status
        self.msg = msg
        self.reason = reason or "The access token is not valid!\n- For more info: " \
                                "https://meapi.readthedocs.io/en/latest/content/setup.html#official-method"


class MeApiError(Enum):
    """
    Enum class for all api errors.
    """
    INCORRECT_PWD_TOKEN = IncorrectPwdToken
    UNFINISHED_REGISTRATION = UnfinishedRegistration
    PHONE_NUMBER_DOESNT_EXISTS = PhoneNumberDoesntExists
    INCORRECT_ACTIVATION_CODE = IncorrectActivationCode
    BLOCKED_MAX_VERIFY_REACHED = BlockedMaxVerifyReached
    MAX_VALIDATE_REACHED = MaxValidateReached
    ACTIVATION_CODE_EXPIRED = ActivationCodeExpired
    SEARCH_PASSED_LIMIT = SearchPassedLimit
    PROFILE_VIEW_PASSED_LIMIT = ProfileViewPassedLimit
    USER_COMMENTS_DISABLED = UserCommentsDisabled
    COMMENT_POSTING_IS_NOT_ALLOWED = UserCommentsPostingIsNotAllowed
    COMMENT_ALREADY_APPROVED = CommentAlreadyApproved
    COMMENT_ALREADY_IGNORED = CommentAlreadyIgnored
    USER_BLOCKED = BlockedAccount
    UNKNOWN = MeApiException

    @classmethod
    def raise_exception(cls, http_status: int, msg: str, reason: Optional[str] = None):
        try:
            exception = cls[msg.replace('api_', '').upper()].value
        except KeyError:
            exception = cls.UNKNOWN.value
        raise exception(http_status, msg, reason)

    @classmethod
    def _missing_(cls, value: object):
        return cls.UNKNOWN.value


class MeException(Exception):
    """
    Raises this exception when something goes wrong.
        - Base class for all library exceptions.

    :param msg: Reason of the exception.
    :type msg: str
    """

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class NotValidPhoneNumber(MeException):
    """Raise this exception when the phone number is not valid."""
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "Phone number must be 11-15 digits long!"


class NotValidAccessToken(MeException):
    """Raise this exception when the access token is not valid."""
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "Access token not valid! (must contains 3 parts separated by '.')"


class ContactHasNoUser(MeException):
    """Raise this exception when the contact has no user."""
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "The contact has no user!"


class FrozenInstance(MeException):
    """
    Raise this exception when trying to change a frozen instance.
        - In some cases, the library uses frozen instances to prevent changing the attributes because in some models, reassigning the attributes will actually change the data on the server.

    :param cls: The class of the frozen instance.
    :type cls: MeModel
    :param attr: The attribute that is trying to be changed.
    :type attr: str
    :param msg: Reason of the exception. override the default message.
    :type msg: str
    """
    def __init__(self, cls: Type['MeModel'], attr: str, msg: Optional[str] = None):
        self.msg = msg or f"Can't modify frozen instance of {cls.__class__.__name__} with attribute '{attr}'!"


class BrokenCredentialsManager(MeException):
    """
    Raise this exception when the credentials manager is broken.
        - Happens when login was successful but the credentials manager not providing the access token.

    :param msg: Reason of the exception.
    :type msg: str
    """
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "It seems that the CredentialsManager does not provide the necessary data!"


class NeedActivationCode(MeException):
    """
    Raise this exception when the activation code is needed.
        - Happens when trying to login to a new account without providing the activation code in the constructor and the client initialized with ``interaction_mode`` = ``False``.

    :param msg: Reason of the exception.
    :type msg: str
    """
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "You need to provide the activation code in the constructor:\n" \
                          "\t- if this is first initialization of the client: Me(phone_number, activation_code)\n" \
                          "\t- if the client is already initialized: me_client.login(activation_code)" \
                          "\n-For more info: https://meapi.readthedocs.io/en/latest/content/setup.html#initialization"


class NotLoggedIn(MeException):
    """
    Raise this exception when the user is not logged in.
        - Happens when trying to call a method after calling ``me_client.logout(args)``

    :param msg: Reason of the exception.
    :type msg: str
    """
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg or "You are not logged in! call me_client.login(args)" \
                          " first or create a new instance of Me class."
