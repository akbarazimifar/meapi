from time import time, localtime, strftime, mktime, strptime
from base64 import b64encode
from datetime import datetime, date
from quopri import encodestring
from random import randint, choice, uniform, random
from re import sub
from typing import Union, Optional
from requests import get
from meapi.utils.exceptions import MeException
from string import ascii_letters, digits
from hashlib import sha256
from os import urandom, path
from meapi.api.raw.account import upload_image_raw

RANDOM_API = "https://random-data-api.com/api"
HEADERS = {'accept-encoding': 'gzip', 'user-agent': 'okhttp/4.9.1', 'content-type': 'application/json; charset=UTF-8'}


def _upload_picture(client: 'Me', image: str) -> str:
    """
    Upload a profile picture from a local file or a direct url.

    :param image: Path or url to the image. for example: ``https://example.com/image.png``, ``/path/to/image.png``.
    :type image: ``str``
    :return: The url of the uploaded image.
    :rtype: ``str``
    """
    if not str(image).startswith("http"):
        if not path.isfile(image):
            raise MeException(f"File {image} does not exist!")
        with open(image, 'rb') as f:
            image_data = f.read()
    else:
        image_data = get(url=str(image)).content
    return upload_image_raw(client, image_data)['url']


def parse_date(date_str: Optional[str], date_only=False) -> Optional[Union[datetime, date]]:
    if date_str is None:
        return date_str
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d' + ('' if date_only else 'T%H:%M:%S%z'))
    return date_obj.date() if date_only else date_obj


def get_img_binary_content(img_url: str) -> Optional[str]:
    try:
        res = get(img_url)
        if res.status_code == 200:
            return b64encode(res.content).decode("utf-8")
    except:
        return None


def encode_string(string: str) -> str:
    return encodestring(string.encode('utf-8')).decode("utf-8")


def _random_date():
    current_year = date.today().year
    start, end, date_format = f'{current_year - 2}-05-12T00:00:11Z', f'{current_year}-06-24T00:00:11Z', '%Y-%m-%dT%H:%M:%S%z'
    try:
        stime = mktime(strptime(start, date_format))
        etime = mktime(strptime(end, date_format))
        ptime = stime + random() * (etime - stime)
        return datetime.strptime(strftime(date_format, localtime(ptime)), date_format).strftime(date_format)
    except ValueError:
        return choice([start, end])


def generate_random_data(contacts=True, calls=True, location=True) -> dict:
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
                    "called_at": _random_date(),
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


def _register_new_account(client) -> str:
    """
    Register new account.
        - Internal function to register new account and return the new UUID.
    """
    if client._account_details:
        account_details: dict = client._account_details
    else:
        print("** This is a new account and you need to register first.")
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
        msg = "** Your profile successfully created! **\n" if client._account_details is None else ""
        if upload_random_data:
            client.upload_random_data()
        else:
            msg += "It my help to upload some data to your account. You can use in client.upload_random_data() or " \
                   "other account methods to activate your account."
        print(msg)
        return results[1].uuid
    raise MeException("Can't update the profile. Please check your input again.")


def _get_session(seed: str, phone_number: int) -> str:
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
    last_digit = int(str(phone_number)[-1])
    a1 = str(int(phone_number * (last_digit + 2)))
    a2 = str(int(int(time()) * (last_digit + 2)))
    a3 = ''.join(choice(ascii_letters + digits) for _ in range(abs(48 - len(a1 + a2) - 2)))
    iv = urandom(16)
    aes = AES.new(sha256(seed.encode()).digest(), AES.MODE_CBC, iv)
    data_to_encrypt = "{}-{}-{}".format(a1, a2, a3).encode()
    padding = (len(data_to_encrypt) % 16) or 16
    final_token = b64encode(iv + aes.encrypt(data_to_encrypt + bytes((chr(padding) * padding).encode())))
    return final_token.decode()
