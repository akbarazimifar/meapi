from enum import Enum
from typing import Optional
from meapi.models.me_model import MeModel


class AuthData(MeModel):
    def __init__(self, access: str, refresh: str, pwd_token: Optional[str] = None):
        self.access = access
        self.refresh = refresh
        self.pwd_token = pwd_token
        super().__init__()


class NewAccountDetails(MeModel):
    """
    Account details for new account registration.

    :param first_name: First name to use.
    :type first_name: ``str``
    :param last_name: Last name to use. *Default:* ``None``.
    :type last_name: ``str`` | ``None``
    :param email: Email to use. *Default:* ``None``.
    :type email: ``str`` | ``None``
    """
    def __init__(self, first_name: str, last_name: Optional[str] = None, email: Optional[str] = None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        super().__init__()


class CallType(Enum):
    MISSED = "missed"
    OUTGOING = "outgoing"
    INCOMING = "incoming"

    @classmethod
    def all(cls):
        return list(map(lambda c: c.value, cls))


class Contact(MeModel):
    def __init__(self,
                 phone_number: int,
                 name: str,
                 date_of_birth: Optional[str] = None,
                 country_code: Optional[str] = None
                 ):
        self.phone_number = phone_number
        self.name = name
        self.date_of_birth = date_of_birth
        self.country_code = country_code
        super().__init__()


class Call(MeModel):
    def __init__(self,
                 name: str,
                 phone_number: int,
                 call_type: str,
                 called_at: str,
                 duration: int,
                 tag: Optional[str] = None
                 ):
        self.name = name
        self.phone_number = phone_number
        self.tag = tag
        self.type = call_type
        self.called_at = called_at
        self.duration = duration
        super().__init__()


class Location(MeModel):
    def __init__(self,
                 latitude: float,
                 longitude: float,
                 ):
        self.location_longitude = longitude
        self.location_latitude = latitude
        super().__init__()
