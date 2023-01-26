from datetime import datetime, date
from logging import getLogger
from re import match
from typing import Tuple, List, Optional, Union, TYPE_CHECKING, Dict
from meapi.api.raw.account import *
from meapi.models.contact import Contact
from meapi.models.profile import Profile
from meapi.models.call import Call
from meapi.models.blocked_number import BlockedNumber
from meapi.models.user import User
from meapi.utils.exceptions import MeApiException, ProfileViewPassedLimit, BlockedAccount
from meapi.utils.helpers import upload_picture
from meapi.utils.randomator import generate_random_data
from meapi.utils.validators import validate_phone_number, validate_schema_types, \
    validate_uuid

if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

_logger = getLogger(__name__)


class AccountMethods:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise TypeError(
            "Account class is not intended to create an instance's but only to be inherited by Me class."
        )

    def phone_search(self: 'Me', phone_number: Union[str, int]) -> Optional[Contact]:
        """
        Get information on any phone number.

        :param phone_number: International phone number format.
        :type phone_number: ``str`` | ``int``
        :raises SearchPassedLimit: if you passed the limit (About ``350`` per day in the unofficial auth method).
        :return: :py:obj:`~meapi.models.contact.Contact` object or ``None`` if no user exists on the provided phone number.
        :rtype: :py:obj:`~meapi.models.contact.Contact` | ``None``
        """
        try:
            response = phone_search_raw(client=self, phone_number=validate_phone_number(phone_number))
        except MeApiException as err:
            if err.http_status == 404:
                return None
            raise err
        return Contact.new_from_dict(response['contact'], _client=self)

    def get_profile(self: 'Me', uuid: Union[str, Contact, User]) -> Profile:
        """
        Get user's profile.

         For Me users (those who have registered in the app) there is an account ``UUID`` obtained when receiving
         information about the phone number :py:func:`phone_search`. With it,
         you can get social information and perform social actions.

        :param uuid: The user's UUID as ``str`` or :py:obj:`~meapi.models.contact.Contact` or :py:obj:`~meapi.models.user.User` objects.
        :type uuid: ``str`` | :py:obj:`~meapi.models.contact.Contact` | :py:obj:`~meapi.models.user.User`
        :raises ProfileViewPassedLimit:  if you passed the limit (About ``500`` per day in the unofficial auth method).
        :return: :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: :py:obj:`~meapi.models.profile.Profile`
        """
        uuid = self._extract_uuid_from_obj(uuid)
        try:
            res = get_profile_raw(client=self, uuid=validate_uuid(str(uuid)))
        except MeApiException as err:
            if isinstance(err, ProfileViewPassedLimit):
                if uuid == self.uuid:
                    _logger.warning('You passed the profile view limit '
                                    '(About 500 per day in the unofficial auth method). You got the limited profile.')
                    return self.get_my_profile(only_limited_data=True)
                err.reason = 'You passed the profile views limit (About 500 per day in the unofficial auth method).'
            raise err
        if uuid == self.uuid:
            res['_my_profile'] = True
        return Profile.new_from_dict(res, _client=self, **res.pop('profile'))

    def get_my_profile(self: 'Me', only_limited_data: bool = False) -> Profile:
        """
        Get your profile information.

        :param only_limited_data: ``True`` to get only limited data (not included in the rate limit). *Default:* ``False``.
        :type only_limited_data: ``bool``
        :return: :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: :py:obj:`~meapi.models.profile.Profile`
        """
        if self.uuid and not only_limited_data:
            res = get_profile_raw(client=self, uuid=self.uuid)
        else:
            res = get_my_profile_raw(client=self)
        try:
            extra = res.pop('profile')
        except KeyError:
            extra = {}
        return Profile.new_from_dict(_client=self, data=res, _my_profile=True, **extra)

    def get_uuid(self: 'Me', phone_number: Union[int, str] = None) -> Optional[str]:
        """
        Get user's uuid (To use in :py:func:`get_profile`, :py:func:`get_comments` and more).

        :param phone_number: International phone number format. Default: None (Return self uuid).
        :type phone_number: ``str`` | ``int`` | ``None``
        :return: String of uuid, or None if no user exists on the provided phone number.
        :rtype: ``str`` | ``None``
        """
        if phone_number:  # others uuid
            res = self.phone_search(phone_number)
            if res and getattr(res, 'user', None):
                return validate_uuid(res.user.uuid)
            return None
        return get_my_profile_raw(client=self)['uuid']

    def update_profile_details(self: 'Me',
                               first_name: Optional[str] = False,
                               last_name: Optional[str] = False,
                               email: Optional[str] = False,
                               gender: Optional[str] = False,
                               slogan: Optional[str] = False,
                               profile_picture: Optional[str] = False,
                               date_of_birth: Optional[Union[str, datetime, date]] = False,
                               location_name: Optional[str] = False,
                               carrier: Optional[str] = False,
                               device_type: Optional[str] = False,
                               login_type: Optional[str] = False,
                               facebook_url: Optional[Union[str, int]] = False,
                               google_url: Optional[Union[str, int]] = False,
                               ) -> Tuple[bool, Profile]:
        """
        Update your profile details.
            - The default of the parameters is ``False``. if you leave it ``False``, the parameter will not be updated.

        Examples:
            >>> me.update_profile_details(first_name='Chandler', last_name='Bing', date_of_birth='1968-04-08')
            >>> new_details = {'location_name': 'New York', 'gender': 'M'}
            >>> me.update_profile_details(**new_details)  # dict unpacking

        :param first_name: First name.
        :type first_name: ``str`` | ``None``
        :param last_name: Last name.
        :type last_name: ``str`` | ``None``
        :param email: For example: ``user@domian.com``.
        :type email: ``str`` | ``None``
        :param gender: ``M`` for male, ``F`` for female.
        :type gender: ``str`` | ``None``
        :param profile_picture: Direct image url or local image path. for example: ``https://example.com/image.png``, ``/home/david/Downloads/my_profile.jpg``.
        :type profile_picture: ``str`` | ``None``
        :param slogan: Your bio.
        :type slogan: ``str`` | ``None``
        :param date_of_birth: date/datetime obj or string with ``YYYY-MM-DD`` format. for example: ``1994-09-22``.
        :type date_of_birth: ``str`` | ``date`` | ``datetime`` | ``None``
        :param location_name: Your location, can be anything.
        :type location_name: ``str`` | ``None``
        :param login_type: ``email`` or ``apple``.
        :type login_type: ``str`` | ``None``
        :param device_type: ``android`` or ``ios``.
        :type device_type: ``str`` | ``None``
        :param carrier: The carrier of your phone. like ``HOT-mobile``, ``AT&T`` etc.
        :param facebook_url: facebook id, for example: ``24898745174639``.
        :type facebook_url: ``str`` | ``int`` | ``None``
        :param google_url: google id, for example: ``24898745174639``.
        :type google_url: ``str`` | ``int`` | ``None``

        :return: Tuple of: Is update success, new :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: Tuple[``bool``, :py:obj:`~meapi.models.profile.Profile`]
        :raises ValueError: If one of the parameters is not valid.
        """
        args = locals()
        del args['self']
        for key, value in args.items():
            if value is not False:
                if key == 'device_type':
                    device_types = ['android', 'ios']
                    if value not in device_types and value is not None:
                        raise ValueError(f"Device type not in the available device types "
                                         f"({', '.join(device_types)}, None)!")
                if key == 'date_of_birth' and value is not None:
                    date_str = str(value)
                    if ' ' in date_str:  # datetime obj
                        date_str = date_str.split(' ')[0]
                    try:
                        datetime.strptime(date_str, '%Y-%M-%d')
                    except ValueError:
                        raise ValueError(f"Birthday must be in YYYY-MM-DD format! {value}")
                    args[key] = date_str
                elif key in ['facebook_url', 'google_url'] and value is not None and not match(r'^\d+$', str(value)):
                    raise ValueError(f"{key} must be numbers!")
                elif key == 'profile_picture':
                    if value is not None:
                        if not isinstance(value, str):
                            raise ValueError("profile_picture_url must be a url or path to a file!")
                        args[key] = str(upload_picture(self, **{'image': value}))
                elif key == 'gender':
                    if value not in ['M', 'm', 'F', 'f', None]:
                        raise ValueError("Gender must be: 'F' for Female, 'M' for Male, and 'None' for null.")
                    args[key] = str(value).upper() if value is not None else None
                elif key in ['first_name', 'last_name', 'slogan', 'location_name'] and type(value) not in [str, None]:
                    raise ValueError(f"{key} value must be a string or None!")
                elif key == 'email':
                    if value is not None and not match(r'^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*'
                                                       r')|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.'
                                                       r',;:\s@\"]{2,})$', str(value)):
                        raise ValueError("Email must be in user@domain.com format!")
                elif key == 'login_type':
                    login_types = ['email', 'apple', None]
                    if value not in login_types:
                        raise ValueError(f"{key} not in the available login types ({', '.join(login_types)})!")

        body = {key: val for key, val in args.items() if val is not False}
        try:
            res = update_profile_details_raw(client=self, **body)
        except MeApiException as err:
            if err.http_status == 401 and err.msg == 'User is blocked for patch':
                raise BlockedAccount(err.http_status, err.msg)
            raise err
        successes = 0
        for key in body.keys():
            if res[key] == body[key]:
                successes += 1
        return bool(successes == len(body.keys())), Profile.new_from_dict(res, _client=self, _my_profile=True)

    def delete_account(self: 'Me', yes_im_sure: bool = False) -> bool:
        """
        Delete your account and it's data (!!!)

        :param yes_im_sure: ``True`` to delete your account and ignore prompt. *Default:* ``False``.
        :type yes_im_sure: ``bool``
        :return: Is deleted.
        :rtype: ``bool``
        """
        if not yes_im_sure:
            print("Are you sure you want to delete your account? (y/n)")
            if input().lower() != 'y':
                return False
        if delete_account_raw(client=self) == {}:
            self._logout()
            return True
        return False

    def suspend_account(self: 'Me', yes_im_sure: bool = False) -> bool:
        """
        Suspend your account until your next login.

        :param yes_im_sure: ``True`` to suspend your account and ignore prompt. *Default:* ``False``.
        :type yes_im_sure: ``bool``
        :return: Is suspended.
        :rtype: ``bool``
        """
        if not yes_im_sure:
            print("Are you sure you want to suspend your account? (y/n)")
            if input().lower() != 'y':
                return False
        if suspend_account_raw(client=self)['contact_suspended']:
            self._logout()
            return True
        return False

    def add_contacts(self: 'Me', contacts: List[Dict[str, Union[str, int, None]]]) -> dict:
        """
        Upload new contacts to your Me account. See :py:func:`upload_random_data`.

        :param contacts: List of dicts with contacts data.
        :type contacts: List[``dict``])
        :return: Dict with upload results.
        :rtype: ``dict``

        Example of list of contacts to add::

            [
                {
                    "country_code": "XX",
                    "date_of_birth": None,
                    "name": "Chandler",
                    "phone_number": 512145887,
                }
            ]
        """
        return add_contacts_raw(client=self, contacts=contacts)

    def remove_contacts(self: 'Me', contacts: List[Dict[str, Union[str, int, None]]]) -> dict:
        """
        Remove contacts from your Me account.

        :param contacts: List of dicts with contacts data.
        :type contacts: List[``dict``]
        :return: Dict with upload results.
        :rtype: ``dict``

        Example of list of contacts to remove::

            [
                {
                    "country_code": "XX",
                    "date_of_birth": None,
                    "name": "Chandler",
                    "phone_number": 512145887,
                }
            ]
        """
        return remove_contacts_raw(client=self, contacts=contacts)

    def get_saved_contacts(self: 'Me') -> List[User]:
        """
        Get all the contacts stored in your contacts (Which has an Me account).

        :return: List of saved contacts.
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        return [usr for grp in self.get_groups() for usr in grp.contacts if usr.in_contact_list]

    def get_unsaved_contacts(self: 'Me') -> List[User]:
        """
        Get all the contacts that not stored in your contacts (Which has an Me account).

        :return: List of unsaved contacts.
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        return [usr for grp in self.get_groups() for usr in grp.contacts if not usr.in_contact_list]

    def add_calls_to_log(self: 'Me', calls: List[Dict[str, Union[str, int, None]]]) -> List[Call]:
        """
        Add call to your calls log. See :py:func:`upload_random_data`.

        :param calls: List of dicts with calls data.
        :type calls: List[``dict``]
        :return: dict with upload result.
        :rtype: ``dict``

        Example of list of calls to add::

            [
                {
                    "called_at": "2021-07-29T11:27:50Z",
                    "duration": 28,
                    "name": "043437535",
                    "phone_number": 43437535,
                    "tag": None,
                    "type": "missed",
                }
            ]
        """
        r = add_calls_raw(client=self, calls=calls)
        return [Call.new_from_dict(cal) for cal in r['added_list']]

    def remove_calls_from_log(self: 'Me', calls: List[Dict[str, Union[str, int, None]]]) -> List[Call]:
        """
        Remove calls from your calls log.

        :param calls: List of dicts with calls data.
        :type calls: List[``dict``]
        :return: dict with upload result.
        :rtype: ``dict``

        Example of list of calls to remove::

            [
                {
                    "called_at": "2021-07-29T11:27:50Z",
                    "duration": 28,
                    "name": "043437535",
                    "phone_number": 43437535,
                    "tag": None,
                    "type": "missed",
                }
            ]
        """
        return [Call.new_from_dict(cal) for cal in remove_calls_raw(client=self, calls=calls)['removed_list']]

    def block_profile(self: 'Me', phone_number: Union[str, int], block_contact=True, me_full_block=True) -> BlockedNumber:
        """
        Block user profile.

        :param phone_number: User phone number in international format.
        :type phone_number: ``str`` | ``int``
        :param block_contact: To block for calls. *Default:* ``True``.
        :type block_contact: ``bool``
        :param me_full_block: To block for social. *Default:* ``True``.
        :type me_full_block: ``bool``
        :return: :py:obj:`~meapi.models.blocked_number.BlockedNumber` object.
        :rtype: :py:obj:`~meapi.models.blocked_number.BlockedNumber`
        """
        body = {'phone_number': validate_phone_number(phone_number), 'block_contact': block_contact, 'me_full_block': me_full_block}
        validate_schema_types({'phone_number': int, 'block_contact': bool, 'me_full_block': bool}, body)
        res = block_profile_raw(client=self, **body)
        if res['success']:
            return BlockedNumber.new_from_dict(body, _client=self)

    def unblock_profile(self: 'Me', phone_number: int, unblock_contact=True, me_full_unblock=True) -> bool:
        """
        Unblock user profile.

        :param phone_number: User phone number in international format.
        :type phone_number: ``str`` | ``int``
        :param unblock_contact: To unblock for calls. *Default:* ``True``.
        :type unblock_contact: ``bool``
        :param me_full_unblock: To unblock for social. *Default:* ``True``.
        :type me_full_unblock: ``bool``
        :return: Is successfully unblocked.
        :rtype: ``bool``
        """
        body = {'phone_number': validate_phone_number(phone_number), 'unblock_contact': unblock_contact, 'me_full_unblock': me_full_unblock}
        validate_schema_types({'phone_number': int, 'unblock_contact': bool, 'me_full_unblock': bool}, body)
        res = unblock_profile_raw(client=self, **body)
        if res['success']:
            return True
        return False

    def block_numbers(self: 'Me', numbers: Union[int, str, List[Union[int, str]]]) -> bool:
        """
        Block phone numbers.

        :param numbers: Single or list of phone numbers in international format.
        :type numbers: ``int`` | ``str`` | List[``int`` | ``str``]
        :return: Is blocked success.
        :rtype: ``bool``
        """
        if isinstance(numbers, (int, str)):
            numbers = [numbers]
        body = {'numbers': [validate_phone_number(number) for number in numbers]}
        return bool([phone['phone_number'] for phone in
                     block_numbers_raw(client=self, **body)].sort() == numbers.sort())

    def unblock_numbers(self: 'Me', numbers: Union[int, List[int]]) -> bool:
        """
        Unblock numbers.

        :param numbers: Single or list of phone numbers in international format. See :py:func:`get_blocked_numbers`.
        :type numbers: ``int`` | List[``int``]
        :return: Is unblocking success.
        :rtype: ``bool``
        """
        if isinstance(numbers, (int, str)):
            numbers = [numbers]
        body = {'numbers': [validate_phone_number(number) for number in numbers]}
        return unblock_numbers_raw(client=self, **body)['success']

    def get_blocked_numbers(self: 'Me') -> List[BlockedNumber]:
        """
        Get list of your blocked numbers. See :py:func:`unblock_numbers`.

        :return: List of :py:class:`blocked_number.BlockedNumber` objects.
        :rtype: List[:py:obj:`~meapi.models.blocked_number.BlockedNumber`]
        """
        return [BlockedNumber.new_from_dict(blocked) for blocked in get_blocked_numbers_raw(client=self)]

    def upload_random_data(self: 'Me', count: int = 50, contacts=False, calls=False, location=False) -> bool:
        """
        Upload random data to your account.

        :param count: Count of random data to upload. Default: ``50``.
        :type count: ``int``
        :param contacts: To upload random contacts data. Default: ``False``.
        :type contacts: ``bool``
        :param calls: To upload random calls data. Default: ``False``.
        :type calls: ``bool``
        :param location: To upload random location data. Default: ``False``.
        :type location: ``bool``
        :return: Is uploading success.
        :rtype: ``bool``
        """
        random_data = generate_random_data(count=count, contacts=contacts, calls=calls, location=location)
        if contacts:
            self.add_contacts([c.as_dict() for c in random_data.contacts])
        if calls:
            self.add_calls_to_log([c.as_dict() for c in random_data.calls])
        if location:
            self.update_location(random_data.location.location_latitude, random_data.location.location_longitude)
        return True
