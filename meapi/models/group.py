from datetime import datetime
from typing import Union, List
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
from meapi.models.contact import Contact
from meapi.models.me_model import MeModel


class Group(MeModel):
    def __init__(self,
                 _meobj,
                 name: Union[str, None] = None,
                 count: Union[int, None] = None,
                 last_contact_at: Union[str, None] = None,
                 contacts: Union[List[dict], None] = None,
                 contact_ids: Union[List[int], None] = None,
                 status: str = "active"
                 ):
        self.name = name
        self.count = count
        self.last_contact_at: Union[datetime, None] = parse_date(last_contact_at)
        self.contacts = [Contact.new_from_json_dict(contact) for contact in contacts] if contacts else contacts
        self.contact_ids = contact_ids
        self.status = status
        self.__meobj = _meobj
        self.__init_done = True

    def __setattr__(self, key, value):
        if getattr(self, '_Group__init_done', None):
            if key != 'status':
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Group name={self.name} count={self.count}>"

    def __str__(self):
        return self.name

    def delete(self) -> bool:
        if self.status != 'active':
            raise MeException(f"The name '{self.name}' is already hidden!")
        if self.__meobj.delete_name(self.contact_ids):
            self.status = 'hidden'
            return True
        return False

    def restore(self) -> bool:
        if self.status != 'hidden':
            raise MeException(f"The name '{self.name}' is already activated!")
        if self.__meobj.restore_name(self.contact_ids):
            self.status = 'active'
            return True
        return False

    def ask_to_rename(self, new_name) -> bool:
        if self.status != 'active':
            raise MeException("You can't ask to rename if the name is hidden. restore and then ask again!")
        if self.__meobj.ask_group_rename(self.contact_ids, new_name):
            return True
        return False
