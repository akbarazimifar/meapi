from re import match, M
from typing import Tuple, List, Optional, TYPE_CHECKING
from meapi.api.raw.account import *
from meapi.utils.validations import validate_contacts, validate_calls, validate_phone_number
from meapi.utils.exceptions import MeApiException, MeException
from meapi.utils.helpers import generate_random_data, _register_new_account, _upload_picture
from meapi.models import contact, profile, call, blocked_number, user
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Account:
    """
    This class is not intended to create an instance's but only to be inherited by ``Me``.
    The separation is for order purposes only.
    """
    def __init__(self: 'Me'):
        raise MeException("Account class is not intended to create an instance's but only to be inherited by Me class.")

    def phone_search(self: 'Me', phone_number: Union[str, int]) -> Optional[contact.Contact]:
        """
        Get information on any phone number.

        :param phone_number: International phone number format.
        :type phone_number: ``str`` | ``int``
        :raises MeApiException: msg: ``api_search_passed_limit`` if you passed the limit (About ``350`` per day in the unofficial auth method).
        :return: :py:obj:`~meapi.models.contact.Contact` object or ``None`` if no user exists on the provided phone number.
        :rtype: :py:obj:`~meapi.models.contact.Contact` | ``None``
        """
        try:
            response = phone_search_raw(self, validate_phone_number(phone_number))
        except MeApiException as err:
            if err.http_status == 404 and err.msg == 'Not found.':
                return None
            else:
                raise err
        return contact.Contact.new_from_dict(response['contact'], _client=self)

    def get_profile(self: 'Me', uuid: Union[str, contact.Contact, user.User]) -> profile.Profile:
        """
        Get user's profile.

         For Me users (those who have registered in the app) there is an account ``UUID`` obtained when receiving
         information about the phone number :py:func:`phone_search`. With it,
         you can get social information and perform social actions.

        :param uuid: The user's UUID as ``str`` or :py:obj:`~meapi.models.contact.Contact` or :py:obj:`~meapi.models.user.User` objects.
        :type uuid: ``str`` | :py:obj:`~meapi.models.contact.Contact` | :py:obj:`~meapi.models.user.User`
        :raises MeApiException: msg: ``api_profile_view_passed_limit`` if you passed the limit (About ``500`` per day in the unofficial auth method).
        :return: :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: :py:obj:`~meapi.models.profile.Profile`
        """
        if isinstance(uuid, contact.Contact):
            if getattr(uuid, 'user', None):
                uuid = uuid.user.uuid
        if isinstance(uuid, user.User):
            uuid = uuid.uuid
        res = get_profile_raw(self, str(uuid))
        if uuid == self.uuid:
            res['_my_profile'] = True
        extra_profile = res.pop('profile')
        return profile.Profile.new_from_dict(res, _client=self, **extra_profile)

    def get_my_profile(self: 'Me') -> profile.Profile:
        """
        Get your profile information.

        :return: :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: :py:obj:`~meapi.models.profile.Profile`
        """
        if self.uuid:
            res = get_profile_raw(self, self.uuid)
        else:
            res = get_my_profile_raw(self)
        try:
            extra = res.pop('profile')
        except KeyError:
            extra = {}
        return profile.Profile.new_from_dict(_client=self, data=res, _my_profile=True, **extra)

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
                return res.user.uuid
            return None
        try:  # self uuid
            return get_my_profile_raw(self)['uuid']
        except MeApiException as err:
            if err.http_status == 401:  # on login, if no active account on this number you need to register
                return _register_new_account(self)
            else:
                raise err

    def update_profile_details(self: 'Me',
                               first_name: str = False,
                               last_name: str = False,
                               email: str = False,
                               gender: str = False,
                               slogan: str = False,
                               profile_picture: str = False,
                               date_of_birth: str = False,
                               location_name: str = False,
                               carrier: str = False,
                               device_type: str = False,
                               login_type: str = False,
                               facebook_url: str = False,
                               google_url: str = False,
                               ) -> Tuple[bool, profile.Profile]:
        """
        Update your profile details.
            - The default of the parameters is ``False``. if you leave it ``False``, the parameter will not be updated.

        :param first_name: First name.
        :type first_name: ``str``
        :param last_name: Last name.
        :type last_name: ``str``
        :param email: For example: ``user@domian.com``.
        :type email: ``str``
        :param gender: ``M`` for male, ``F`` for female.
        :type gender: ``str``
        :param profile_picture: Direct image url or local image path. for example: ``https://example.com/image.png``, ``/home/david/Downloads/my_profile.jpg``.
        :type profile_picture: ``str``
        :param slogan: Your bio.
        :type slogan: ``str``
        :param date_of_birth: ``YYYY-MM-DD`` format. for example: ``1997-05-15``.
        :type date_of_birth: ``str``
        :param location_name: Your location, can be anything.
        :type location_name: ``str``
        :param login_type: ``email`` or ``apple``.
        :type login_type: ``str``
        :param device_type: ``android`` or ``ios``.
        :type device_type: ``str``
        :param carrier: The carrier of your phone. like ``HOT-mobile``, ``AT&T`` etc.
        :param facebook_url: facebook id, for example: ``24898745174639``.
        :type facebook_url: ``str`` | ``int``
        :param google_url: google id, for example: ``24898745174639``.
        :type google_url: ``str`` | ``int``

        :return: Tuple of: Is update success, new :py:obj:`~meapi.models.profile.Profile` object.
        :rtype: Tuple[``bool``, :py:obj:`~meapi.models.profile.Profile`]
        """
        args = locals()
        del args['self']
        for key, value in args.items():
            if value is not False:
                if key == 'device_type':
                    device_types = ['android', 'ios', None]
                    if value not in device_types:
                        raise MeException(f"Device type not in the available device types ({', '.join(device_types)})!")
                if key == 'date_of_birth' and value is not None and not match(r'^\d{4}(\-)(((0)\d)|((1)[0-2]))(\-)([0-2]\d|(3)[0-1])$', flags=M, string=str(value)):
                    raise MeException("Birthday must be in YYYY-MM-DD format!")
                elif key in ['facebook_url', 'google_url'] and value is not None and not match(r'^\d+$', str(value)):
                    raise MeException(f"{key} must be numbers!")
                elif key == 'profile_picture':
                    if value is not None:
                        if not isinstance(value, str):
                            raise MeException("profile_picture_url must be a url or path to a file!")
                        args[key] = str(_upload_picture(self, **{'image': value}))
                elif key == 'gender':
                    if value not in ['M', 'm', 'F', 'f', None]:
                        raise MeException("Gender must be: 'F' for Female, 'M' for Male, and 'None' for null.")
                    if value:
                        args[key] = str(value).upper()
                elif key in ['first_name', 'last_name', 'slogan', 'location_name'] and type(value) not in [str, None]:
                    raise MeException(f"{key} value must be a string or None!")
                elif key == 'email':
                    if value is not None and not match(r'^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$', str(value)):
                        raise MeException("Email must be in user@domain.com format!")
                elif key == 'login_type':
                    login_types = ['email', 'apple', None]
                    if value not in login_types:
                        raise MeException(f"{key} not in the available login types ({', '.join(login_types)})!")

        body = {key: val for key, val in args.items() if val is not False}
        try:
            res = update_profile_details_raw(self, **body)
        except MeApiException as err:
            if err.http_status == 401 and err.msg == 'User is blocked for patch':
                err.reason = "Locks like your account is blocked!"
            raise err
        successes = 0
        for key in body.keys():
            if res[key] == body[key]:
                successes += 1
        return bool(successes == len(body.keys())), profile.Profile.new_from_dict(res, _client=self, _my_profile=True)

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
        if delete_account_raw(self) == {}:
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
        if suspend_account_raw(self)['contact_suspended']:
            self._logout()
            return True
        return False

    def add_contacts(self: 'Me', contacts: List[dict]) -> dict:
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
        return add_contacts_raw(self, validate_contacts(contacts))

    def remove_contacts(self: 'Me', contacts: List[dict]) -> dict:
        """
        Remove contacts from your Me account.

        :param contacts: List of dicts with contacts data.
        :type contacts: List[``dict``]
        :return: Dict with upload results.
        :rtype: ``dict``
        """
        return remove_contacts_raw(self, validate_contacts(contacts))

    def get_saved_contacts(self: 'Me') -> List[user.User]:
        """
        Get all the contacts stored in your contacts (Which has an Me account).

        :return: List of saved contacts.
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        return [usr for grp in self.get_groups() for usr in grp.contacts if usr.in_contact_list]

    def get_unsaved_contacts(self: 'Me') -> List[user.User]:
        """
        Get all the contacts that not stored in your contacts (Which has an Me account).

        :return: List of unsaved contacts.
        :rtype: List[:py:obj:`~meapi.models.user.User`]
        """
        return [usr for grp in self.get_groups() for usr in grp.contacts if not usr.in_contact_list]

    def add_calls_to_log(self: 'Me', calls: List[dict]) -> List[call.Call]:
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
        body = {"add": validate_calls(calls), "remove": []}
        r = self._make_request('post', '/main/call-log/change-sync/', body)
        return [call.Call.new_from_dict(cal) for cal in r['added_list']]

    def remove_calls_from_log(self: 'Me', calls: List[dict]) -> List[call.Call]:
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
        body = {"add": [], "remove": validate_calls(calls)}
        return [call.Call.new_from_dict(cal) for cal in self._make_request('post', '/main/call-log/change-sync/', body)]

    def block_profile(self: 'Me', phone_number: Union[str, int], block_contact=True, me_full_block=True) -> blocked_number.BlockedNumber:
        """
        Block user profile.

        :param phone_number: User phone number in international format.
        :type phone_number: ``str`` | ``int``
        :param block_contact: To block for calls. *Default:* ``True``.
        :type block_contact: ``bool``
        :param me_full_block: To block for social. *Default:* ``True``.
        :type me_full_block: ``bool``
        :return: :py:obj:`meapi.models.blocked_number.BlockedNumber` object.
        :rtype: :py:obj:`meapi.models.blocked_number.BlockedNumber`
        """
        res = block_profile_raw(client=self, phone_number=validate_phone_number(phone_number), me_full_block=me_full_block, block_contact=block_contact)
        if res['success']:
            return blocked_number.BlockedNumber.new_from_dict(**res, _client=self)

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
        res = unblock_profile_raw(client=self, phone_number=validate_phone_number(phone_number), me_full_unblock=me_full_unblock, unblock_contact=unblock_contact)
        if res['success']:
            return True
        return False

    def block_numbers(self: 'Me', numbers: Union[int, List[int]]) -> bool:
        """
        Block phone numbers.

        :param numbers: Single or list of phone numbers in international format.
        :type numbers: ``int`` | List[``int``]
        :return: Is blocked success.
        :rtype: ``bool``
        """
        if not isinstance(numbers, list) and isinstance(numbers, int):
            numbers = [numbers]
        return bool([phone['phone_number'] for phone in block_numbers_raw(self, numbers)].sort() == numbers.sort())

    def unblock_numbers(self: 'Me', numbers: Union[int, List[int]]) -> bool:
        """
        Unblock numbers.

        :param numbers: Single or list of phone numbers in international format. See :py:func:`get_blocked_numbers`.
        :type numbers: ``int`` | List[``int``]
        :return: Is unblocking success.
        :rtype: ``bool``
        """
        if not isinstance(numbers, list):
            numbers = [numbers]
        return unblock_numbers_raw(self, numbers)['success']

    def get_blocked_numbers(self: 'Me') -> List[blocked_number.BlockedNumber]:
        """
        Get list of your blocked numbers. See :py:func:`unblock_numbers`.

        :return: List of :py:class:`blocked_number.BlockedNumber` objects.
        :rtype: List[:py:obj:`~meapi.models.blocked_number.BlockedNumber`]
        """
        return [blocked_number.BlockedNumber.new_from_dict(blocked) for blocked in get_blocked_numbers_raw(self)]

    def upload_random_data(self: 'Me', contacts=True, calls=True, location=True) -> bool:
        """
        Upload random data to your account.

        :param contacts: To upload random contacts data. Default: ``True``.
        :type contacts: ``bool``
        :param calls: To upload random calls data. Default: ``True``.
        :type calls: ``bool``
        :param location: To upload random location data. Default: ``True``.
        :type location: ``bool``
        :return: Is uploading success.
        :rtype: ``bool``
        """
        random_data = generate_random_data(contacts, calls, location)
        if contacts:
            self.add_contacts(random_data['contacts'])
        if calls:
            self.add_calls_to_log(random_data['calls'])
        if location:
            self.update_location(random_data['location']['lat'], random_data['location']['lon'])
        return True
