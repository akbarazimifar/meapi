⚙️ Setup
=========

⬇️ Installation
---------------
.. include:: ../../../README.rst
  :start-after: installation
  :end-before: end-installation

========================================================================

🎛️ Initialization
-------------------
There are two ways to initialize the :py:obj:`~meapi.Me` client. *the programmatic way* and *the interactive way*.

💻 The programmatic way
.......................

Here you will need to provide the phone number and the activation code and also try to catch the exceptions that may occur.

- This method is more suitable for automation, for example if you want to interact with the client from a web server.

    >>> from meapi import Me
    >>> me = Me(phone_number=1234567890, activation_code='123456', interactive_mode=False) # intractive_mode=False is the default value
    >>> my_profile = me.get_my_profile() # start using the client

You may want to catch some exceptions that may occur during the initialization process:

    >>> from meapi import Me
    >>> try:
    ...     me = Me(phone_number=1234567890, activation_code='123456', interactive_mode=False)
    ... except NewAccountException: # If this is a new number that is not already open an account
    ...     me = Me(phone_number=1234567890, new_account_details=NewAccountDetails(
    ...         first_name="Chandler",
    ...         last_name="Bing",
    ...         email="chandler.bing@friends.tv"
    ...     ))
    >>> my_profile = me.get_my_profile() # start using the client

- See the exceptions that may occur in the initialization process of the :py:obj:`~meapi.Me` class (in the ``raises`` section).


✍️ The interactive way
.......................

Here you will be prompted to choose the authentication method and then you will be prompted to enter the necessary information.

- This method is more suitable for self use, for testing and for thous who are not familiar with the library.

>>> from meapi import Me
>>> me = Me(interactive_mode=True)
Welcome to Meapi!
How do you want to login?"
    1. Unofficial method (phone number)
    2. Official method (access token)
Enter your choice (1-2): 1
Enter your phone number: 1234567890
To get access token you need to authorize yourself.
Enter your verification code (6 digits): 123456
>>> my_profile = me.get_my_profile() # start using the client


========================================================================

🔐 Authentication
-----------------

No matter the initialization method you choose, you will need to authenticate yourself in order to use the client.
There are two ways for authentication, the unofficial method and the official method.

✅ Unofficial method
.....................

*important notes:*

    - **This method is for educational purposes only and its use is at your own risk.** See `disclaimer <https://meapi.readthedocs.io/en/latest/index.html#disclaimer>`_.
    - In this method you are going to verify as a user of the app and get a token with access to all the actions that the app provides.
    - After verification, if you are connected to another device, Chances are you will be disconnected.
    - For app users there is an Rate-limit of about ``350`` phone searches and ``500`` profile views per day.


- There are two forms of active authentication, which means that you can initialize the client with the authentication code that you will receive actively in one of the following forms:
    1. **WhatsApp:** Go to `WhatsApp <https://wa.me/447427928793?text=Connectme>`_ and send any message to this number (`+447427928793 <tel:+447427928793>`_) to get a verification code.
    2. **Telegram:** Go to Telegram (http://t.me/Meofficialbot?start=__iw__XXXXXX Replace the ``XXXXX`` with your phone number) and hit ``/start`` to get a verification code.

- After you get the code, you can initialize the client with the following code:

>>> from meapi import Me
>>> me = Me(phone_number=1234567890, activation_code='123456')

- If this is a new number that is not already open an account, you will be required to fill in some details like name and email in order to create an account, See `Registration <https://meapi.readthedocs.io/en/latest/content/setup.html#id2>`_.

🔓 Official method
...................

- You can also use the official verification and verify directly with an access token.
    Me has an official API which can be accessed by submitting a formal request at `this <https://meapp.co.il/api/>`_ link (Probably paid).
    I guess you get a API KEY with which you can get an access token similar to the app.
    But I do not know what the scope of this token are and whether it is possible to contact with it the same endpoints that the official app addresses.
- If anyone can shed light on the official authentication method, I would be happy if he would `contact me <https://t.me/davidlev>`_. so that I could better support it and exclude or add certain functions.
- If you have an access token and you are interested in connecting with it - do the following:

.. code-block:: python

    from meapi import Me
    me = Me(access_token='XXXXXXXXXX') # Enter your access token

Keep in mind that the access token is valid for 24 hours, and to meapi it is not possible to refresh it without the ``phone_number`` and ``pwd_token``,
So you will need to catch the :py:obj:`~meapi.utils.exceptions.ForbiddenRequest` exception and reinitialize the client with a new access token.

.. code-block:: python

    from meapi import Me
    from meapi.utils.exceptions import ForbiddenRequest

    me = Me(access_token='XXXXXXXXXX')

    try:
        do_something_with_me()
    except ForbiddenRequest:
        access_token = your_own_implementation_of_getting_new_access_token()
        me = Me(access_token=access_token)


- Again, if you have any information about the process of getting an access token in official method, contact me and I will be happy to add it to the library.

========================================================================

🔌 Registration
-----------------

Because the authentication in Meapi is active (you don't sit and wait for the code, but initializing the client with the phone number and the activation code you have already received actively),
You can also initialize the client with the necessary information in advance, good for cases of creating a new account:


.. code-block:: python

    from meapi import Me
    from meapi.models.others import NewAccountDetails

    data = NewAccountDetails(
        first_name="Phoebe
        last_name="Buffay",
        email="reginaphalange@friends.tv"
    )

    me = Me(
        phone_number=972123456789,
        activation_code='123456',
        new_account_details=data
    )

If you don't know if this is a new account, try except for :py:obj:`~meapi.utils.exceptions.NewAccountException`:

.. code-block:: python

    from meapi import Me
    from meapi.models.others import NewAccountDetails
    from meapi.utils.exceptions import NewAccountException

    try:
        me = Me(phone_number=972123456789, activation_code='123456')
    except NewAccountException:
        data = NewAccountDetails( # Ask the user for the details
            first_name=input("Enter first name: "),
            last_name=input("Enter last name: "),
            email=input("Enter email: ") or None
        )
        # no need to for the activation code because the credentials are already saved
        me = Me(phone_number=972123456789, new_account_details=data)

    # Continue using the client

========================================================================

🔑 Credentials
---------------
meapi, needs to store your credentials (access token, refresh token etc.) in order to be able to use them later on without the need to login again every time you want to use the API.

- The default credentials manager is the - :py:obj:`~meapi.credentials_managers.json_files.JsonCredentialsManager`, which saves the credentials in a json file (``meapi_credentials.json`` by default).
- You can implement your own credentials manager by implementing the :py:obj:`~meapi.credentials_managers.CredentialsManager` interface. See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_.
- If you choose to use in the default credentials manager, the config file will be created in the location from which the library was called.
- The config file ``meapi_credentials.json`` format is:

.. code-block:: json

    {
        "972123456789": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.XXXXX",
            "pwd_token": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXXXXXXX",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.XXXXX"
        }
    }

- You can copy/move this file between projects. Just specify the path to the config file in when you initialize the Me class:

.. code-block:: python

    from meapi import Me
    from meapi.credentials_managers.json_files import JsonCredentialsManager

    cm = JsonCredentialsManager(config_file="/home/david/meapi_credentials.json")
    me = Me(phone_number=123456789, credentials_manager=cm)


📞 SMS or Call
---------------

    Many ask me why there is no option to verify via SMS or call.

    Well, This is because authentication via WhatsApp and Telegram, is action of the user who sends a message to the bot and receives
    the verification code, as opposed to a call or SMS that requires an external service (which of course costs money) to make
    the call or send the SMS.

    This is why at the app level, ``Me`` Apps used a secret key to generates a time-based hashed session token.

    For obvious reasons I can not provide the key, but if you have knowledge of extracting secrets from APKs, look for the key and export
    it in the environment variables with the key ``ANTI_SESSION_BOT_KEY``.
    meapi will detect the presence of the environment and offer you to use authentication via SMS or call.

- Needless to say, the functionality is for educational purposes only.
