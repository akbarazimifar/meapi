from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from meapi.models.user import User
from meapi.utils.exceptions import FrozenInstance
from meapi.utils.helpers import parse_date
from meapi.models.me_model import MeModel, _logger
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me


class Group(MeModel):
    """
    Represents a group of users that save you in their contact list in the same name
        - `For more information about this feature <https://me.app/who-saved-my-number/>`_

    Examples:
        >>> my_groups = me.get_groups()
        >>> group = my_groups[0]
        >>> group.name
        'Phoebe Buffay'
        >>> group.count
        6
        >>> group.last_contact_at
        datetime.datetime(2004, 5, 6, 21, 0)
        >>> group.ask_to_rename(new_name='Regina Phalange')

    Parameters:
        name (``str``):
            The name of the group, how your number saved in their contact list.
        count (``int``):
            The number of users in the group.
        last_contact_at (``datetime`` *optional*):
            The last time that you saved in someone's contact list.
        contacts (List[:py:obj:`~meapi.models.user.User`]):
            The users that are in the group.
        contact_ids (``List[int]``):
            The ids of the users that are in the group.
        is_active (``bool``):
            Is the group active.
            - You can use :py:func:`~meapi.models.group.Group.delete` to hide the group and :py:func:`~meapi.models.group.Group.restore` to restore it.

    Methods:

    .. automethod:: delete
    .. automethod:: restore
    .. automethod:: ask_to_rename
    """
    def __init__(self,
                 _client: 'Me',
                 name: str = None,
                 count: int = None,
                 last_contact_at: str = None,
                 contacts: List[dict] = None,
                 contact_ids: List[int] = None,
                 is_active: bool = True
                 ):
        self.name = name
        self.count = count
        self.last_contact_at: Optional[datetime] = parse_date(last_contact_at)
        self.contacts = [User.new_from_dict(contact.get('user'), id=contact.get('id'), in_contact_list=contact.get('in_contact_list'))
                         for contact in contacts] if contacts else contacts
        self.contact_ids = contact_ids
        self.is_active = is_active
        self.__client = _client
        self.__init_done = True

    def delete(self) -> bool:
        """
        Deletes the group.
            - The same as :py:func:`~meapi.Me.delete_group`.
            - You get ``True`` even if the group is already hidden.

        Returns:
            ``bool``: ``True`` if the group was deleted, ``False`` otherwise.
        """
        if not self.is_active:
            _logger.info(f"DELETE_GROUP: Group '{self.name}' is already deleted.")
            return True
        if self.__client.delete_group(self.contact_ids):
            self.is_active = False
            return True
        return False

    def restore(self) -> bool:
        """
        Restores the group.
            - The same as :py:func:`~meapi.Me.restore_group`.
            - You get ``True`` even if the group is already active.

        Returns:
            ``bool``: ``True`` if the group was restored, ``False`` otherwise.
        """
        if self.is_active:
            _logger.info(f"RESTORE_GROUP: Group '{self.name}' is already restored.")
            return True
        if self.__client.restore_group(self.contact_ids):
            self.is_active = True
            return True
        return False

    def ask_to_rename(self, new_name) -> bool:
        """
        Asks from the users in the group to rename you in their contact list.
            - The same as :py:func:`~meapi.Me.ask_group_rename`.
            - You can't adk rename a group if it's hidden (``is_active=False``).

        Parameters:
            new_name (``str``):
                The new name that you want them to rename you in their contact list.

        Returns:
            ``bool``: ``True`` if the suggested send, ``False`` otherwise.
        """
        if not self.is_active:
            _logger.warning(f"ASK_GROUP_RENAME: Group '{self.name}' is not active, restore it first.")
            return False
        if self.__client.ask_group_rename(self.contact_ids, new_name):
            return True
        return False

    def __setattr__(self, key, value):
        if getattr(self, '_Group__init_done', None):
            if key != 'is_active':
                raise FrozenInstance(self, key)
        return super().__setattr__(key, value)
