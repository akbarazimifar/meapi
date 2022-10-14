⚒ Raw
=====

The next page contains raw functions that accept an instance of ``Me`` in the first parameter, make an API call and return raw data.
meapi maps the data to objects, but these functions can be accessed manually:

.. code-block:: python

    from meapi.api.raw.account import phone_search_raw, get_profile_raw
    from meapi import Me

    me = Me(972123456789) # initialize the client

    search_res = phone_search_raw(me, 972987654321)
    profile_res = get_profile_raw(me, 'fdsfs-fdsfs-fdsfs-fdsfs')

🔐 Auth
--------
.. automodule:: meapi.api.raw.auth
   :members:
   :undoc-members:
   :show-inheritance:

👤 Account
-----------
.. automodule:: meapi.api.raw.account
   :members:
   :undoc-members:
   :show-inheritance:

🌐 Social
----------
.. automodule:: meapi.api.raw.social
   :members:
   :undoc-members:
   :show-inheritance:

⚙️Settings
----------
.. automodule:: meapi.api.raw.settings
   :members:
   :undoc-members:
   :show-inheritance:

🔔 Notifications
----------------
.. automodule:: meapi.api.raw.notifications
   :members:
   :undoc-members:
   :show-inheritance:
