from meapi.utils.exceptions import MeException
from meapi.utils.helpers import as_vcard


class _CommonMethodsForUserContactProfile:
    """
    Common methods for user, profile and contact.
    """
    def get_profile(self):
        """
        Returns the profile of the contact.

        Returns:
            :py:obj:`~meapi.models.profile.Profile` | ``None``: The profile of the contact or ``None`` if the contact has no user.
        """
        if hasattr(self, 'user'):
            if getattr(self, 'user', None):
                uuid = self.user.uuid
            else:
                return None
        else:
            uuid = self.uuid
        return getattr(self, f'_{self.__class__.__name__}__client').get_profile(uuid)

    def block(self, block_contact=True, me_full_block=True) -> bool:
        """
        Block a contact.

        Parameters:
            block_contact: (``bool``):
                If you want to block the contact from calls. *Default:* ``True``.
            me_full_block: (``bool``):
                If you want to block the contact from Me platform. *Default:* ``True``.

        Returns:
            ``bool``: ``True`` if the contact was blocked successfully, else ``False``.
        """
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't block yourself!")
        return getattr(self, f'_{self.__class__.__name__}__client').block_profile(phone_number=self.phone_number, block_contact=block_contact, me_full_block=me_full_block)

    def unblock(self, unblock_contact=True, me_full_unblock=True) -> bool:
        """
        Unblock a contact.

        Parameters:
            unblock_contact: (``bool``):
                If you want to unblock the contact from calls. *Default:* ``True``.
            me_full_unblock: (``bool``):
                If you want to unblock the contact from Me platform. *Default:* ``True``.

        Returns:
            ``bool``: ``True`` if the contact was unblocked successfully, else ``False``.
        """
        if getattr(self, f'_{self.__class__.__name__}__my_profile', None):
            raise MeException("you can't unblock yourself!")
        return getattr(self, f'_{self.__class__.__name__}__client').unblock_profile(phone_number=self.phone_number, unblock_contact=unblock_contact, me_full_unblock=me_full_unblock)

    def report_spam(self, spam_name: str, country_code: str) -> bool:
        """
        Report this contact as spam.
            - The same as :py:func:`~meapi.Me.report_spam`.

        Parameters:
            spam_name: (``str``):
                Name of the spammer.
            country_code: (``str``):
                Country code of the spammer.

        Returns:
            ``bool``: ``True`` if the contact was reported successfully, else ``False``.
        """
        return getattr(self, f'_{self.__class__.__name__}__client').report_spam(phone_number=self.phone_number, spam_name=spam_name, country_code=country_code)

    def as_vcard(self, prefix_name: str = "", dl_profile_picture: bool = True, **kwargs) -> str:
        """
        Get contact data in vcard format in order to add it to your contacts book.

        Example:
            .. code-block:: python

                uuids = ['xx-xx-xx-xx', 'yy-yy-yy-yy', 'zz-zz-zz-zz']
                profiles = [me.get_profile(uuid) for uuid in uuids] # can raise rate limit exception.
                vcards = [profile.as_vcard(prefix_name="Imported - ", dl_profile_picture=False,
                    twitter='social.twitter.profile_id', gender='gender') for profile in profiles]
                with open('contacts.vcf', 'w') as contacts:
                    contacts.write('\\n'.join(vcards))

        Parameters:
            prefix_name: (``str``):
                If you want to add prefix to the name of the contact, like ``Mr.``, ``Mrs.``, ``Imported`` etc. *Default:* empty string ``""``.
            dl_profile_picture: (``bool``):
                If you want to download and add profile picture to the vcard (if available). *Default:* ``True``.
            kwargs:
                Add any other data to the ``notes`` field of the vcard. The key must be, of course, exists in the object as attr eith value of ``str`` or ``int``.
                    - For example, if you want to add a gender information to the contact, you can pass the parameter ``gender='gender'``
                    - The key uses as the title in the notes (you name it as you like), and the value is the attribute name of the object.
                    - You can go even deeper: if Profile object provided, you may want to do something like ``twitter='social.twitter.profile_id'``.
                    - No exception will be raised if the key doesn't exist.

        Returns:
            ``str``: Vcard format as string. See `Wikipedia <https://en.wikipedia.org/wiki/VCard#Properties>`_ for more information.
        """
        return as_vcard(self, prefix_name, dl_profile_picture, **kwargs)

