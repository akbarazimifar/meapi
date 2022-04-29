🔗 Reference
=============


Reference for the Me class.

.. currentmodule:: meapi
.. autoclass:: Me


🔎 Search
---------
.. automethod:: Me.phone_search
.. automethod:: Me.get_profile_info
.. automethod:: Me.get_uuid

👤 Account
-----------

.. automethod:: Me.update_profile_info
.. automethod:: Me.add_contacts
.. automethod:: Me.get_saved_contacts
.. automethod:: Me.get_unsaved_contacts
.. automethod:: Me.remove_contacts
.. automethod:: Me.add_calls_to_log
.. automethod:: Me.remove_calls_from_log
.. automethod:: Me.block_profile
.. automethod:: Me.unblock_profile
.. automethod:: Me.block_numbers
.. automethod:: Me.unblock_numbers
.. automethod:: Me.get_blocked_numbers
.. automethod:: Me.upload_random_data
.. automethod:: Me.suspend_account
.. automethod:: Me.delete_account

🌐 Social
----------
.. automethod:: Me.friendship
.. automethod:: Me.suggest_turn_on_mutual
.. automethod:: Me.report_spam
.. automethod:: Me.who_deleted
.. automethod:: Me.who_watched
.. automethod:: Me.is_spammer
.. automethod:: Me.get_age
.. automethod:: Me.numbers_count

📱 Social network
------------------
.. automethod:: Me.get_socials
.. automethod:: Me.add_social
.. automethod:: Me.remove_social
.. automethod:: Me.switch_social_status

👥 Group names
---------------
.. automethod:: Me.get_groups_names
.. automethod:: Me.delete_name
.. automethod:: Me.get_deleted_names
.. automethod:: Me.restore_name
.. automethod:: Me.ask_group_rename

💬 Comments
------------
.. automethod:: Me.get_comments
.. automethod:: Me.suggest_turn_on_comments
.. automethod:: Me.get_comment
.. automethod:: Me.publish_comment
.. automethod:: Me.approve_comment
.. automethod:: Me.delete_comment
.. automethod:: Me.like_comment

📍 Location
------------
.. automethod:: Me.update_location
.. automethod:: Me.suggest_turn_on_location
.. automethod:: Me.share_location
.. automethod:: Me.get_distance
.. automethod:: Me.stop_sharing_location
.. automethod:: Me.stop_shared_location
.. automethod:: Me.locations_shared_by_me
.. automethod:: Me.locations_shared_with_me

🔔 Notifications
----------------
.. automethod:: Me.unread_notifications_count
.. automethod:: Me.get_notifications
.. automethod:: Me.read_notification

⚙️Settings
----------
.. automethod:: Me.get_settings
.. automethod:: Me.change_social_settings
.. automethod:: Me.change_notification_settings

❗ Exceptions
-------------
.. currentmodule:: meapi.exceptions
.. autoclass:: MeApiException
.. autoclass:: MeException

🛠 Utils
--------
**These methods are for internal use but can still be used if you wish.**

.. currentmodule:: meapi
.. automethod:: Me.make_request
.. automethod:: Me.valid_phone_number

🔐 Auth
--------
**These methods are for internal use but can still be used if you wish.**

.. automethod:: Me.activate_account
.. automethod:: Me.generate_access_token
.. automethod:: Me.credentials_manager
