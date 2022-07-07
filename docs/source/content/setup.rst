⚙️ Setup
=========

⬇️ Installation
---------------
.. include:: ../../../README.rst
  :start-after: installation
  :end-before: end-installation


🔐 Authentication
-----------------

✅ Unofficial method
^^^^^^^^^^^^^^^^^^^^^
**important notes:**

    - **This method is for educational purposes only and its use is at your own risk.** See `disclaimer <https://meapi.readthedocs.io/en/latest/index.html#disclaimer>`_.
    - In this method you are going to verify as a user of the app and get a token with access to all the actions that the app provides.
    - After verification, if you are connected to another device, Chances are you will be disconnected.
    - For app users there is an Rate-limit of about ``350`` phone searches and ``500`` profile views per day.

**Verification:**

- Run this code:

.. code-block:: python

    from meapi import Me
    me = Me(phone_number=1234567890) # Enter your phone number

- If you have not verified this number before, you will see the following prompt in the terminal:

::

    To get access token you need to authorize yourself:
    * WhatsApp (Recommended): https://wa.me/972543229534?text=Connectme
    * Telegram: http://t.me/Meofficialbot?start=__iw__XXXXXXXXXX // Your phone number instead of the 'XXXXX'

    ** Enter your verification code (6 digits):

- Go into `WhatsApp <https://wa.me/972543229534?text=Connectme>`_ (+972543229534) and send any message to this number.
- You can also verify by Me Telegram bot (Only if you have Telegram account on this number!) and get verification code of 6 digits.
- Enter the code in the terminal and you will see if the verification was successful.
- If this is a new number that is not already open an account, you will be required to fill in some details like name and email in order to create an account.
- If you keep getting ``404`` error, you may want to run the :py:func:`~meapi.Me.upload_random_data` function, in order to activate the account.

**Registration:**

- You can also initialize the client with the necessary information in advance, good for cases of creating a new account:

.. code-block:: python

    from meapi import Me

    data = {
        'phone_number': 972123456789, # Required always
        'activation_code': '123456', # Required only for the first time
        'first_name': 'Regina', # Required for first account registration
        'last_name': 'Phalange', # Optional for first account registration
        'email': 'kenadams@friends.tv', # Optional for first account registration
        'upload_random_data': True, # Recommended for first account registration. Default: True
        'credentials_manager': None, # Optional. Default: JsonFileCredentialsManager('config.json')
        'session': None, # Optional. Default: new requests.Session()
        'proxies': None, # Optional. Default: None
    }

    me = Me(account_details=data)

**SMS or Call:**

    Many ask me why there is no option to verify via SMS or call.

    Well, This is because authentication via WhatsApp and Telegram, is action of the user who sends a message to the bot and receives
    the verification code, as opposed to a call or SMS that requires an external service (which of course costs money) to make
    the call or send the SMS.

    This is why at the app level, ``Me`` Apps used a secret key to generates a time-based hashed session token.

    For obvious reasons I can not provide the key, but if you have knowledge of extracting secrets from APKs, look for the key and export
    it in the environment variables with the key ``ANTI_SESSION_BOT_KEY``.
    meapi will detect the presence of the environment and offer you to use authentication via SMS or call.

- Needless to say, the functionality is for educational purposes only.

**Credentials:**

- The default credentials manager is the JsonFileCredentialsManager, which saves the credentials in a json file ('config.file' by default).
- You can implement your own credentials manager by implementing the CredentialsManager interface. See `Credentials Manager <https://meapi.readthedocs.io/en/latest/content/credentials_manager.html>`_.
- If you choose to use in the default credentials manager, If no path to the config file is provided, the config file will be created in the location from which the library was called.
- The config file ``config.json`` format is:

.. literalinclude:: ../../../config.json.example
  :language: JSON

- You can copy/move this file between projects. Just specify the path to the config file when you initialize the Me class:

.. code-block:: python

    from meapi import Me
    me = Me(phone_number=123456789, config_file="/home/david/credentials/config.json")

🔓 Official method
^^^^^^^^^^^^^^^^^^^

- You can also use the official verification and verify directly with an access token.
    Me has an official API which can be accessed by submitting a formal request at `this <https://meapp.co.il/api/>`_ link (Probably paid).
    I guess you get a API KEY with which you can get an access token similar to the app.
    But I do not know what the scope of this token are and whether it is possible to contact with it the same endpoints that the official app addresses.
- If anyone can shed light on the official authentication method, I would be happy if he would `contact me <https://t.me/davidlev>`_. so that I could better support it and exclude or add certain functions.
- If you have an access token and you are interested in connecting with it - do the following:

.. code-block:: python

    from meapi import Me
    me = Me(access_token='XXXXXXXXXX') # Enter your access token

