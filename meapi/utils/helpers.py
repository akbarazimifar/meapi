import time
from base64 import b64encode
from datetime import datetime, date
from quopri import encodestring
from random import randint, choice, uniform, random
from re import sub
from typing import Union
from requests import get
from meapi.utils.exceptions import MeException

RANDOM_API = "https://random-data-api.com/api"


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


def get_vcard(data: dict, prefix_name: str = "", profile_picture: bool = True, **kwargs) -> str:
    """
    Get vcard format based on data provided
    """
    vcard_data = {'start': "BEGIN:VCARD", 'version': "VERSION:3.0"}

    if prefix_name:
        prefix_name += " - "
    full_name = (prefix_name + (data.get('first_name') or data.get('name')))
    if data.get('last_name'):
        full_name += (" " + data['last_name'])

    vcard_data['name'] = f"FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(full_name)}"
    vcard_data['phone'] = f"TEL;CELL:{data['phone_number']}"
    if profile_picture and data.get('profile_picture'):
        vcard_data['photo'] = f"PHOTO;ENCODING=BASE64;JPEG:{get_img_binary_content(data['profile_picture'])}"
    if data.get('email'):
        vcard_data['email'] = f"EMAIL:{data['email']}"
    if data.get('date_of_birth'):
        vcard_data['birthday'] = f"BDAY:{data['date_of_birth']}"

    notes = 'Extracted by meapi https://github.com/david-lev/meapi'
    for key, value in kwargs.items():
        if data.get(key):
            notes += f" | {value}: {data[key]}"

    vcard_data['note'] = f"NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:{encode_string(notes)}"
    vcard_data['end'] = "END:VCARD"

    return "\n".join([val for val in vcard_data.values()])


def random_date():
    date_format = '%Y-%m-%dT%H:%M:%S%z'
    stime = time.mktime(time.strptime('2020-05-12T00:00:11Z', date_format))
    etime = time.mktime(time.strptime('2022-06-24T00:00:11Z', date_format))
    ptime = stime + random() * (etime - stime)
    return datetime.strptime(time.strftime(date_format, time.localtime(ptime)), date_format).strftime(date_format)


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
