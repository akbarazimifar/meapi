🗄 Credentials Manager
======================

**The credentials manager allows you to store your credentials in your own way.**

There are number of credentials managers that are already implemented in the project:

- ``JsonCredentialsManager`` (Used by default) that stores the credentials in a json file (``meapi_credentials.json`` by default),
- ``RedisCredentialsManager`` that stores the credentials in a redis database.
- ``MemoryCredentialsManager`` that stores the credentials in memory.
- ``FlaskSessionCredentialsManager`` that stores the credentials in a flask session.
- ``DjangoSessionCredentialsManager`` that stores the credentials in a django session.


* You are more than welcome to create your own credentials manager and open a pull request to add it to the project.

---------------------------------

➕ **Creating your own custom CredentialsManager:**

- You must implement the methods ``get``, ``set``, ``update`` and ``delete`` in order to allow ``Me`` to store and manage the credentials.

.. currentmodule:: meapi.credentials_managers
.. autoclass:: CredentialsManager()
    :members:
    :undoc-members:

---------------------------------

📄 **Examples:**

Let's say you want to store the credentials in a database, create a new class that implements the ``CredentialsManager`` interface:

.. code-block:: python

    from meapi.credentials_manager import CredentialsManager
    from typing import Optional

    class DatabaseCredentialsManager(CredentialsManager):
        def __init__(self, db_connection):
            self.db_connection = db_connection
        def get(self, phone_number: str) -> Optional[dict]:
            return self.db_connection.get_credentials(phone_number)
        def set(self, phone_number: str, data: dict):
            self.db_connection.set_credentials(phone_number, data)
        def update(self, phone_number: str, access_token: str):
            self.db_connection.update_credentials(phone_number, access_token)
        def delete(self, phone_number: str):
            self.db_connection.clear_credentials(phone_number)


You can use the credentials manager in the following way:

    >>> from me import Me
    >>> me = Me(phone_number=972123456789, credentials_manager=DatabaseCredentialsManager(db_connection))

Here is another example of how to store the credentials in redis:

.. literalinclude:: ../../../meapi/credentials_managers/redis.py
    :language: python


- And this is how you can use it:

    >>> from me import Me
    >>> from redis import Redis
    >>> from meapi.utils.credentials_managers import RedisCredentialsManager
    >>> redis = Redis(host='localhost', port=6379, db=0)
    >>> me = Me(phone_number=972123456789, credentials_manager=RedisCredentialsManager(redis))

