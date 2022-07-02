from datetime import datetime
from typing import Union, List
from meapi.models.user import User
from meapi.utils.exceptions import MeException
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel


class Group(MeModel):
    """
    Represents a group of users that save you in their contact list in the same name
        - `For more information about this feature: <https://me.app/who-saved-my-number/>`_

    Parameters:
        name (``str``):
            The name of the group, how you save in their contact list.
        count (``int``):
            The number of users in the group.
        last_contact_at (``datetime`` *optional*):
            The last time that you saved in someone's contact list.
        contacts (List[:py:obj:`~meapi.models.user.User`]):
            The users that are in the group.
        contact_ids (``List[int]``):
            The ids of the users that are in the group.
        status (``str``):
            The status of the group, can be ``active`` or ``hidden``.

    Methods:

    .. automethod:: delete
    .. automethod:: restore
    .. automethod:: ask_to_rename
    """
    def __init__(self,
                 _client,
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
        self.contacts = [User.new_from_dict(contact['user']) for contact in contacts] if contacts else contacts
        self.contact_ids = contact_ids
        self.status = status
        self.__client = _client
        self.__init_done = True

    def delete(self) -> bool:
        """
        Deletes the group.
            - The same as :py:func:`~meapi.Me.delete_group`.

        Returns:
            ``bool``: ``True`` if the group was deleted, ``False`` otherwise.
        """
        if self.status != 'active':
            raise MeException(f"The name '{self.name}' is already hidden!")
        if self.__client.delete_name(self.contact_ids):
            self.status = 'hidden'
            return True
        return False

    def restore(self) -> bool:
        """
        Restores the group.
            - The same as :py:func:`~meapi.Me.restore_group`.

        Returns:
            ``bool``: ``True`` if the group was restored, ``False`` otherwise.
        """
        if self.status != 'hidden':
            raise MeException(f"The name '{self.name}' is already activated!")
        if self.__client.restore_name(self.contact_ids):
            self.status = 'active'
            return True
        return False

    def ask_to_rename(self, new_name) -> bool:
        """
        Asks from the users in the group to rename you in their contact list.
            - The same as :py:func:`~meapi.Me.ask_group_rename`.

        Parameters:
            new_name (``str``):
                The new name that you want them to rename you in their contact list.

        Returns:
            ``bool``: ``True`` if the suggested send, ``False`` otherwise.
        """
        if self.status != 'active':
            raise MeException("You can't ask to rename if the name is hidden. restore and then ask again!")
        if self.__client.ask_group_rename(self.contact_ids, new_name):
            return True
        return False

    def __setattr__(self, key, value):
        if getattr(self, '_Group__init_done', None):
            if key != 'status':
                raise MeException("You can't change this attr!")
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"<Group name={self.name} count={self.count}>"

    def __str__(self):
        return self.name
