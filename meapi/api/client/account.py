from re import match
from typing import Union, Tuple, List
from meapi.api.raw.account import *
from meapi.utils.validations import validate_contacts, validate_calls, validate_phone_number
from meapi.utils.exceptions import MeApiException, MeException
from meapi.utils.helpers import get_random_data
from meapi.models import contact, profile, call, blocked_number


class Account:

    def phone_search(self, phone_number: Union[str, int]) -> Union[contact.Contact, None]:
        """
        Get information on any phone number.

        :param phone_number: International phone number format.
        :type phone_number: Union[str, int])
        :raises MeApiException: msg: ``api_search_passed_limit`` if you passed the limit (About 350 per day in the unofficial auth method).
        :return: Contact object.
        :rtype: Contact
        """
        try:
            response = phone_search_raw(self, validate_phone_number(phone_number))
        except MeApiException as err:
            if err.http_status == 404 and err.msg == 'Not found.':
                return None
            else:
                raise err
        return contact.Contact.new_from_json_dict(response['contact'])

    def get_profile(self, uuid: Union[str, None]) -> profile.Profile:
        """
        Get user profile info.

        For Me users (those who have registered in the app) there is an account UUID obtained when receiving
        information about the phone number :py:func:`phone_search`. With it, you can get social information
        and perform social actions.

        :param uuid: uuid of the Me user.
        :type uuid: str
        :raises MeApiException: msg: ``api_profile_view_passed_limit`` if you passed the limit (About 500 per day in the unofficial auth method).
        :return: Profile object.
        :rtype: Profile
        """
        res = get_profile_raw(self, str(uuid))
        if uuid == self.uuid:
            res['_my_profile'] = True
        extra_profile = res.pop('profile')
        return profile.Profile.new_from_json_dict(res, _meobj=self, **extra_profile)

    def get_my_profile(self) -> profile.Profile:
        """
        Get your profile information.

        :return: Profile object.
        :rtype: Profile
        """
        if self.uuid:
            res = get_profile_raw(self, self.uuid)
        else:
            res = get_my_profile_raw(self)
        try:
            extra = res.pop('profile')
        except KeyError:
            extra = {}
        return profile.Profile.new_from_json_dict(_meobj=self, data=res, _my_profile=True, **extra)

    def _register(self) -> str:
        """
        Register new account.
        """
        print("** This is a new account and you need to register first.")
        if self.account_details:
            account_details: dict = self.account_details
        else:
            account_details = {}
        first_name = None
        last_name = None
        email = None
        upload_random_data = None

        if account_details.get('first_name'):
            first_name = account_details['first_name']
        else:
            while not first_name:
                first_name = input("* Enter your first name (Required): ")

        if account_details.get('last_name'):
            last_name = account_details['last_name']
        elif not account_details:
            last_name = input("* Enter your last name (Optional): ")

        if account_details.get('email'):
            email = account_details['email']
        elif not account_details:
            email = input("* Enter your email (Optional): ") or None

        if account_details.get('upload_random_data'):
            upload_random_data = account_details['upload_random_data']
        elif not account_details:
            answer = "X"
            while answer.upper() not in ['Y', 'N', '']:
                answer = input("* Do you want to upload some random data (contacts, calls, location) in order "
                               "to initialize the account? (Enter is Y) [Y/N]: ")
            if answer.upper() in ["Y", ""]:
                upload_random_data = True
            else:
                upload_random_data = False

        results = self.update_profile_info(first_name=first_name, last_name=last_name, email=email, login_type='email')
        if results[0]:
            msg = "** Your profile successfully created!"
            if upload_random_data:
                self.upload_random_data()
                msg += "\n* But you may not be able to perform searches for a few hours. It my help to " \
                       "upload some data. You can use in me.upload_random_data() or other account methods to " \
                       "activate your account."
            print(msg)
            return self.get_uuid()
        raise MeException("Can't update the following details: " + ", ".join(results[1]))

    def get_uuid(self, phone_number: Union[int, str] = None) -> Union[str, None]:
        """
        Get user's uuid (To use in :py:func:`get_profile`, :py:func:`get_comments` and more).

        :param phone_number: International phone number format. Default: None (Return self uuid).
        :type phone_number: Union[str, int, None]
        :return: String of uuid, or None if no user exists on the provided phone number.
        :rtype: Union[str, None]
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
                return self._register()
            else:
                raise err

    def update_profile_info(self, country_code: str = None,
                            date_of_birth: str = None,
                            device_type: str = None,
                            login_type: str = None,
                            email: str = None,
                            facebook_url: str = None,
                            first_name: str = None,
                            last_name: str = None,
                            gender: str = None,
                            profile_picture_url: str = None,
                            slogan: str = None) -> Tuple[bool, list]:
        """
        Update profile information.

        :param login_type: ``email``. Default: ``None``
        :type login_type: str
        :param country_code: Your phone number country_code (``972`` = ``IL`` etc.) // `Country codes <https://countrycode.org/>`_. Default: ``None``
        :type country_code: str
        :param date_of_birth: ``YYYY-MM-DD`` format. for example: ``1997-05-15``. Default: ``None``
        :type date_of_birth: str
        :param device_type: ``android`` / ``ios``. Default: ``None``
        :type device_type: str
        :param email: For example: ``name@domian.com``. Default: ``None``
        :type email: str
        :param facebook_url: facebook id, for example: ``24898745174639``. Default: ``None``
        :type facebook_url: Union[str, int]
        :param first_name: First name. Default: ``None``
        :type first_name: str
        :param last_name: Last name. Default: ``None``
        :type last_name: str
        :param gender: ``M`` for male, ``F`` for and ``N`` for None. Default: ``None``
        :type gender: str
        :param profile_picture_url: Direct image url. for example: ``https://example.com/image.png``. Default: ``None``
        :type profile_picture_url: str
        :param slogan: Your bio. Default: ``None``
        :type slogan: str
        :return: Tuple of: is update success, list of failed.
        :rtype: Tuple[bool, list]
        """
        device_types = ['android', 'ios']
        genders = {'M': 'M', 'F': 'F', 'N': None}
        body = {}
        if country_code is not None:
            body['country_code'] = str(country_code).upper()[:2]
        if date_of_birth is not None:
            if not match(r"^\d{4}(\-)([0-2][0-9]|(3)[0-1])(\-)(((0)[0-9])|((1)[0-2]))$", str(date_of_birth)):
                raise MeException("Date of birthday must be in YYYY-MM-DD format!")
            body['date_of_birth'] = str(date_of_birth)
        if str(device_type) in device_types:
            body['device_type'] = str(device_type)
        if login_type is not None:
            body['login_type'] = str(login_type)
        if match(r"^\S+@\S+\.\S+$", str(email)):
            body['email'] = str(email)
        if match(r"^\d+$", str(facebook_url)):
            body['facebook_url'] = str(facebook_url)
        if first_name is not None:
            body['first_name'] = str(first_name)
        if last_name is not None:
            body['last_name'] = str(last_name)
        if gender is not None:
            if str(gender).upper() in genders.keys():
                body['gender'] = genders.get(str(gender.upper()))
            else:
                raise MeException("Gender must be: 'F' for female, 'M' for Male, and 'N' for null.")
        if match(r"(https?:\/\/.*\.(?:png|jpg))", str(profile_picture_url)):
            body['profile_picture'] = profile_picture_url
        if slogan is not None:
            body['slogan'] = str(slogan)

        if not body:
            raise MeException("You must change at least one detail!")

        res = self._make_request('patch', '/main/users/profile/', body)
        return res
        failed = []
        for key in body.keys():
            if results[key] != body[key] and key != 'profile_picture':
                # Can't check if profile picture updated because Me convert's it to their own url.
                # you can check before and after.. get_settings()
                failed.append(key)
        return not bool(failed), failed

    def delete_account(self) -> bool:
        """
        Delete your account and it's data (!!!)

        :return: Is deleted.
        :rtype: bool
        """
        return True if not delete_account_raw(self) else False

    def suspend_account(self) -> bool:
        """
        Suspend your account until your next login.

        :return: is suspended.
        :rtype: bool
        """
        return suspend_account_raw(self)['contact_suspended']

    def add_contacts(self, contacts: List[dict]) -> dict:
        """
        Upload new contacts to your Me account. See :py:func:`upload_random_data`.

        :param contacts: List of dicts with contacts data.
        :type contacts: List[dict])
        :return: Dict with upload results.
        :rtype: dict

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

    def remove_contacts(self, contacts: List[dict]) -> dict:
        """
        Remove contacts from your Me account.

        :param contacts: List of dicts with contacts data.
        :type contacts: List[dict])
        :return: Dict with upload results.
        :rtype: dict
        """
        return remove_contacts_raw(self, validate_contacts(contacts))

    def get_saved_contacts(self) -> List[contact.Contact]:
        """
        Get all the contacts stored in your contacts (Which has an Me account).

        :return: List of saved contacts.
        :rtype: List[Contact]
        """
        return [contact for group in self.get_groups_names() for contact in group.contacts if contact.in_contact_list]

    def get_unsaved_contacts(self) -> List[contact.Contact]:
        """
        Get all the contacts that not stored in your contacts (Which has an Me account).

        :return: List unsaved contacts.
        :rtype: List[Contact]
        """
        return [contact for group in self.get_groups_names() for contact in group.contacts if not contact.in_contact_list]

    def add_calls_to_log(self, calls: List[dict]) -> List[call.Call]:
        """
        Add call to your calls log. See :py:func:`upload_random_data`.

        :param calls: List of dicts with calls data.
        :type calls: List[dict]
        :return: dict with upload result.
        :rtype: dict

        Example of list of calls to add::

            [
                {
                    "called_at": "2021-07-29T11:27:50Z",
                    "duration": 28,
                    "name": "043437535",
                    "phone_number": 43437535,
                    "tag": None,
                    "type": "missed",
                },
                {
                    "called_at": "2021-08-08T19:42:59Z",
                    "duration": 0,
                    "name": "Chandler",
                    "phone_number": 334324324,
                    "tag": None,
                    "type": "outgoing",
                },
                {
                    "called_at": "2022-01-03T16:50:24Z",
                    "duration": 15,
                    "name": "Joey",
                    "phone_number": 51495043537,
                    "tag": None,
                    "type": "incoming",
                },
            ]
        """
        body = {"add": validate_calls(calls), "remove": []}
        r = self._make_request('post', '/main/call-log/change-sync/', body)
        return [call.Call.new_from_json_dict(cal) for cal in r['added_list']]

    def remove_calls_from_log(self, calls: List[dict]) -> List[call.Call]:
        """
        Remove calls from your calls log.

        :param calls: List of dicts with calls data.
        :type calls: List[dict]
        :return: dict with upload result.
        :rtype: dict

        Example of list of calls to remove::

            [
                {
                    "called_at": "2021-07-29T11:27:50Z",
                    "duration": 28,
                    "name": "043437535",
                    "phone_number": 43437535,
                    "tag": None,
                    "type": "missed",
                },
                {
                    "called_at": "2021-08-08T19:42:59Z",
                    "duration": 0,
                    "name": "Chandler",
                    "phone_number": 334324324,
                    "tag": None,
                    "type": "outgoing",
                },
                {
                    "called_at": "2022-01-03T16:50:24Z",
                    "duration": 15,
                    "name": "Joey",
                    "phone_number": 51495043537,
                    "tag": None,
                    "type": "incoming",
                },
            ]
        """
        body = {"add": [], "remove": validate_calls(calls)}
        return [call.Call.new_from_json_dict(cal) for cal in self._make_request('post', '/main/call-log/change-sync/', body)]

    def block_profile(self, phone_number: Union[str, int], block_contact=True, me_full_block=True) -> bool:
        """
        Block user profile.

        :param phone_number: User phone number in international format.
        :type phone_number: Union[str, int]
        :param block_contact: To block for calls. Default: ``True``.
        :type block_contact: bool
        :param me_full_block: To block for social. Default: ``True``.
        :type me_full_block: bool
        :return: Is successfully blocked.
        :rtype: bool
        """
        body = {'phone_number': int(validate_phone_number(phone_number)),
                'block_contact': block_contact,
                'me_full_block': me_full_block}
        res = block_profile_raw(meobj=self, **body)
        if res['success']:
            return blocked_number.BlockedNumber.new_from_json_dict(**body)

    def unblock_profile(self, phone_number: int, unblock_contact=True, me_full_unblock=True) -> bool:
        """
        Unblock user profile.

        :param phone_number: User phone number in international format.
        :type phone_number: Union[str, int]
        :param unblock_contact: To unblock for calls. Default: ``True``.
        :type unblock_contact: bool
        :param me_full_unblock: To unblock for social. Default: ``True``.
        :type me_full_unblock: bool
        :return: Is successfully unblocked.
        :rtype: bool
        """
        body = {'phone_number': int(validate_phone_number(phone_number)),
                'unblock_contact': unblock_contact,
                'me_full_unblock': me_full_unblock}
        res = unblock_profile_raw(meobj=self, **body)
        if res['success']:
            return True
        return False

    def block_numbers(self, numbers: Union[int, List[int]]) -> bool:
        """
        Block phone numbers.

        :param numbers: Single or list of phone numbers in international format.
        :type numbers: Union[int, List[int]])
        :return: Is blocked success.
        :rtype: bool
        """
        if not isinstance(numbers, list) and isinstance(numbers, int):
            numbers = [numbers]
        return bool([phone['phone_number'] for phone in block_numbers_raw(self, numbers)].sort() == numbers.sort())

    def unblock_numbers(self, numbers: Union[int, List[int]]) -> bool:
        """
        Unblock numbers.

        :param numbers: Single or list of phone numbers in international format. See :py:func:`get_blocked_numbers`.
        :type numbers: Union[int, List[int]])
        :return: Is unblocking success.
        :rtype: bool
        """
        if not isinstance(numbers, list):
            numbers = [numbers]
        return unblock_numbers_raw(self, numbers)['success']

    def get_blocked_numbers(self) -> List[blocked_number.BlockedNumber]:
        """
        Get list of your blocked numbers. See :py:func:`unblock_numbers`.

        :return: list of BlockedNumber objects.
        :rtype: List[BlockedNumber]
        """
        return [blocked_number.BlockedNumber.new_from_json_dict(blocked) for blocked in get_blocked_numbers_raw(self)]

    def upload_random_data(self, contacts=True, calls=True, location=True):
        """
        Upload random data to your account.

        :param contacts: To upload random contacts data. Default: ``True``.
        :type contacts: bool
        :param calls: To upload random calls data. Default: ``True``.
        :type calls: bool
        :param location: To upload random location data. Default: ``True``.
        :type location: bool
        :return: Is uploading success.
        :rtype: bool
        """
        random_data = get_random_data(contacts, calls, location)
        if contacts:
            self.add_contacts(random_data['contacts'])
        if calls:
            self.add_calls_to_log(random_data['calls'])
        if location:
            self.update_location(random_data['location']['lat'], random_data['location']['lon'])
