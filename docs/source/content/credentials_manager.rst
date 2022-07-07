🗄 Credentials Manager
======================

The credentials manager allows you to store your credentials in your own way.

- For example, if you want to store the credentials in a database, create a new class that implements the ``CredentialsManager`` interface:

.. code-block:: python

    from meapi.utils.credentials_manager import CredentialsManager

    class DatabaseCredentialsManager(CredentialsManager):
        def __init__(self, db_connection):
            self.db_connection = db_connection
        def get(self, phone_number) -> dict:
            return self.db_connection.get_credentials(phone_number)  # do your thing and return the credentials in dict format
        def set(self, phone_number, data):
            self.db_connection.set_credentials(phone_number, data)
        def update(self, phone_number, access_token):
            self.db_connection.update_credentials(phone_number, access_token)
        def delete(self, phone_number):
            self.db_connection.clear_credentials(phone_number)

- You must implement the methods get, set, update and delete in order to allow ``Me`` to store and manage your credentials.

You can use the credentials manager in the following way:

    >>> from me import Me
    >>> me = Me(phone_number=972123456789, credentials_manager=DatabaseCredentialsManager(db_connection))

Here is another example of how to store the credentials in redis:

.. code-block:: python

    from json import dumps, loads
    from meapi.utils.credentials_manager import CredentialsManager

    class RedisCredentialsManager(CredentialsManager):
    """
    Redis Credentials Manager.
        - This class is used to store the credentials in a redis cache.
    """
    def __init__(self, redis):
        self.redis = redis

    def get(self, phone_number: str) -> Union[dict, None]:
        data = self.redis.get(str(phone_number))
        if data:
            return loads(data)
        return None

    def set(self, phone_number: str, data: dict):
        self.redis.set(str(phone_number), dumps(data))

    def update(self, phone_number: str, access_token: str):
        existing_content = loads(self.redis.get(str(phone_number)))
        existing_content['access'] = access_token
        self.redis.set(str(phone_number), dumps(existing_content))

    def delete(self, phone_number: str):
        self.redis.delete(str(phone_number))

- And this is how you can use it:

    >>> from me import Me
    >>> from redis import Redis
    >>> from meapi.utils.credentials_managers import RedisCredentialsManager
    >>> redis = Redis(host='localhost', port=6379, db=0)
    >>> me = Me(phone_number=972123456789, credentials_manager=RedisCredentialsManager(redis))

There are two built-in credentials managers: `JsonFileCredentialsManager` that stores the credentials in a json file and, and
`RedisCredentialsManager` that stores the credentials in a redis database.
- You more than welcome to create your add your own credentials manager and open a pull request to add it to the project.
