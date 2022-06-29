from meapi.utils.exceptions import MeException
from meapi.utils.helpers import get_vcard


class _CommonMethodsForUserContactProfile:
    """
    Common methods for user, profile and contact
    """
    def block(self, block_contact=True, me_full_block=True) -> bool:
        """
        - Block a contact.

        Parameters:
            block_contact: (``bool``):
                If you want to block the contact from calls. *Default: True*
            me_full_block: (``bool``):
                If you want to block the contact from Me platform. *Default: True*

        Returns:
            ``bool``: ``True`` if the contact was blocked successfully, else ``False``.
        """
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't block yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').block_profile(phone_number=self.phone_number, block_contact=block_contact, me_full_block=me_full_block)

    def unblock(self, unblock_contact=True, me_full_unblock=True) -> bool:
        """
        - Unblock a contact.

        Parameters:
            unblock_contact: (``bool``):
                If you want to unblock the contact from calls. *Default: True*
            me_full_unblock: (``bool``):
                If you want to unblock the contact from Me platform. *Default: True*

        Returns:
            ``bool``: ``True`` if the contact was unblocked successfully, else ``False``.
        """
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't unblock yourself!")
        return getattr(self, f'_{self.__class__.__name__}__meobj').unblock_profile(phone_number=self.phone_number, unblock_contact=unblock_contact, me_full_unblock=me_full_unblock)

    def get_vcard(self, prefix_name: str = "", profile_picture: bool = True, **kwargs) -> str:
        """
        - Get contact data in vcard format in order to add it to your contacts book.

        Example:
            .. code-block:: python

                uuids = ['xx-xx-xx-xx', 'yy-yy-yy-yy', 'zz-zz-zz-zz']
                profiles = [me.get_profile(uuid) for uuid in uuids]
                vcards = [profile.get_vcard(prefix_name="Imported", profile_picture=False,
                    birthday='Birthday: ', gender='Gender: ') for profile in profiles]
                with open('contacts.vcf', 'w') as contacts:
                    contacts.write('\\n'.join(vcards))

        Parameters:
            prefix_name: (``str``):
                If you want to add prefix to the name of the contact, like "Mr.", "Mrs.", "Imported" etc. *Default: ""*
            profile_picture: (``bool``):
                If you want to download and add profile picture to the vcard (if available). *Default: True*
            kwargs: (``dict``):
                Add any other data to the ``notes`` field of the vcard. The key must be, of course, exists in the object.

        Returns:
            ``str``: String data in vcard format.
        """
        return get_vcard(self.__dict__, prefix_name, profile_picture, **kwargs)

