from time import time, localtime, strftime, mktime, strptime
from base64 import b64encode
from datetime import datetime, date
from functools import reduce
from quopri import encodestring
from random import randint, choice, uniform, random
from re import sub
from typing import Union
from requests import get
from meapi.utils.exceptions import MeException
from string import ascii_letters, digits
from hashlib import sha256
from os import urandom


RANDOM_API = "https://random-data-api.com/api"
HEADERS = {'accept-encoding': 'gzip', 'user-agent': 'okhttp/4.9.1', 'content-type': 'application/json; charset=UTF-8'}


def parse_date(date_str: Union[str, None], date_only=False) -> Union[datetime, date, None]:
    if date_str is None:
        return date_str
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date_obj.date() if date_only else date_obj


def get_img_binary_content(url: str):
    try:
        res = get(url)
        if res.status_code == 200:
            return b64encode(res.content).decode("utf-8")
    except Exception:
        return None


def encode_string(string: str) -> str:
    return encodestring(string.encode('utf-8')).decode("utf-8")


def as_vcard(data, prefix_name: str = "", dl_profile_picture: bool = True, **kwargs) -> str:
    """
    Get vcard format based on data provided.

    :param data: Profile, Contact or User objects.
    :type data: :py:obj:`~meapi.models.contact.Contact` | :py:obj:`~meapi.models.user.User` | :py:obj:`~meapi.models.profile.Profile`
    :param prefix_name: Prefix name for the name of the contact.
    :type prefix_name: str
    :param dl_profile_picture: Download profile picture of the user and save it in the vcard. *Default:* ``True``.
    :type dl_profile_picture: bool
    :param kwargs: Add any other data to the ``notes`` field of the vcard. The key must be, of course, exists in the object as attr eith value of ``str`` or ``int``.
        - The key uses as the title in the notes (you name it as you like), and the value is the attribute name of the object.
        - You can go even deeper: if Profile object provided, you may want to do something like ``twitter='social.twitter.profile_id'``.
        - No exception will be raised if the key doesn't exist.
    :return: Vcard format as string.
        - See `Wikipedia <https://en.wikipedia.org/wiki/VCard#Properties>`_ for more information.
    :rtype: str
    """
    vcard_data = {'start': "BEGIN:VCARD", 'version': "VERSION:3.0"}
    full_name = prefix_name + (data.name or f'Unknown - {data.phone_number}')
    vcard_data['name'] = f"FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(full_name)}"
    vcard_data['phone'] = f"TEL;CELL:{data.phone_number}"
    if dl_profile_picture and getattr(data, 'profile_picture', None):
        binary = get_img_binary_content(data.profile_picture)
        if binary:
            vcard_data['photo'] = f"PHOTO;ENCODING=BASE64;JPEG:{binary}"
    if getattr(data, 'email', None):
        vcard_data['email'] = f"EMAIL:{data.email}"
    if getattr(data, 'date_of_birth', None):
        vcard_data['birthday'] = f"BDAY:{data.date_of_birth}"

    notes = 'Extracted with meapi <https://github.com/david-lev/meapi>' if not kwargs.get('remove_credit', False) else ''
    for key, value in kwargs.items():
        try:
            attr_value = reduce(getattr, value.split('.'), data)
            if attr_value and isinstance(attr_value, (str, int)):
                notes += f" | {str(key).replace('_', ' ').title()}: {attr_value}"
        except AttributeError:
            continue

    vcard_data['note'] = f"NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(notes)}"
    vcard_data['end'] = "END:VCARD"

    return "\n".join([val for val in vcard_data.values()])


def random_date():
    start, end, date_format = '2020-05-12T00:00:11Z', '2022-06-24T00:00:11Z', '%Y-%m-%dT%H:%M:%S%z'
    try:
        stime = mktime(strptime(start, date_format))
        etime = mktime(strptime(end, date_format))
        ptime = stime + random() * (etime - stime)
        return datetime.strptime(strftime(date_format, localtime(ptime)), date_format).strftime(date_format)
    except ValueError:
        return choice([start, end])


def get_random_data(contacts=True, calls=True, location=True) -> dict:
    if not contacts and not calls and not location:
        raise MeException("You need to set True at least one of the random data types")

    call_types = ['missed', 'outgoing', 'incoming']
    random_data = {}

    if contacts or calls:
        count = randint(30, 50)
        random_numbers = [phone['phone_number'] for phone in get(url=RANDOM_API+f'/phone_number/random_phone_number?size={count}"').json()]
        random_names = [name['name'] for name in get(url=RANDOM_API+f'/name/random_name?size={count}').json()]

        if contacts:
            random_data['contacts'] = []
            for contact in range(1, count + 1):
                random_data['contacts'].append({
                    "country_code": "XX",
                    "date_of_birth": None,
                    "name": str(choice(random_names)),
                    "phone_number": int(sub(r'\D', '', str(choice(random_numbers))))
                })

        if calls:
            random_data['calls'] = []
            for call in range(1, count + 1):
                random_data['calls'].append({
                    "called_at": random_date(),
                    "duration": randint(10, 300),
                    "name": str(choice(random_names)),
                    "phone_number": int(sub(r'\D', '', str(choice(random_numbers)))),
                    "tag": None,
                    "type": choice(call_types)
                })

    if location:
        random_data['location'] = {}
        random_data['location']['lat'] = - round(uniform(30, 60), 5)
        random_data['location']['lon'] = round(uniform(30, 60), 5)

    return random_data


def register_new_account(client) -> str:
    """
    Register new account.
        - Internal function to register new account.
    """
    print("** This is a new account and you need to register first.")
    if client.account_details:
        account_details: dict = client.account_details
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

    results = client.update_profile_details(first_name=first_name, last_name=last_name, email=email, login_type='email')
    if results[0]:
        msg = "** Your profile successfully created! **\n\n* You may not be able to perform searches for a few hours."
        if upload_random_data:
            client.upload_random_data()
        else:
            msg += "It my help to upload some data to your account. You can use in me.upload_random_data() or " \
                   "other account methods to activate your account."
        print(msg)
        return results[1].uuid
    raise MeException("Can't update the profile. Please check your input again.")


def get_session(seed: str, phone_number: int) -> Union[str, None]:
    """
    Generate session token to use in order to get sms or call in the authentication process.

    :param seed: The AntiSessionBot key from the APK (You need to extract it yourself).
    :type seed: str
    :param phone_number: Your phone number in international format.
    :type phone_number: int
    :raises: :py:exc:`~meapi.utils.exceptions.MeException` If the 'Crypto' package isn't installed.
    :return: Session token.
    :rtype: str
    """
    try:
        from Crypto.Cipher import AES
    except ImportError:
        raise MeException('You need to install the `Crypto` package in order to generate session token!')
    string_material = ascii_letters + digits
    anti_session_bot_key = sha256(seed.encode()).digest()
    last_digit = int(str(phone_number)[-1])
    current_time = int(time())
    a1 = str(int(phone_number * (last_digit + 2)))
    a2 = str(int(current_time * (last_digit + 2)))
    len_a1_a2 = len(a1 + a2)
    length_rand_string = abs(48 - len_a1_a2 - 2)
    a3 = ''.join(choice(string_material) for _ in range(length_rand_string))
    result = "{}-{}-{}".format(a1, a2, a3)
    iv = urandom(16)
    aes = AES.new(anti_session_bot_key, AES.MODE_CBC, iv)
    data_to_encrypt = result.encode()
    padding = len(data_to_encrypt) % 16
    if padding == 0:
        padding = 16
    enc_data = aes.encrypt(data_to_encrypt + bytes((chr(padding) * padding).encode()))
    final_token = b64encode(iv + enc_data)
    return final_token.decode()
