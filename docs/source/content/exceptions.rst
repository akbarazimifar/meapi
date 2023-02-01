❗ Exceptions
=============

**This is a list of all exceptions that may be raised by the library.**

*On the top level, there are two exceptions:*

* :py:obj:`~meapi.utils.exceptions.MeApiException`: Raised when the API returns an error.
* :py:obj:`~meapi.utils.exceptions.MeException`: Raised when the library itself has an error.

It is recommended to catch :py:obj:`~meapi.utils.exceptions.MeApiException` and :py:obj:`~meapi.utils.exceptions.MeException` separately.
Here is an example:

.. code-block:: python

    from meapi import Me
    from meapi.utils.exceptions import *

    # Getting some user input:
    phone_number = input("Enter your phone number: ")
    activation_code = input("Enter your activation code: ")

    try:
        me = Me(phone_number=phone_number, activation_code=activation_code)
    except MeApiException as e:
        if isinstance(e, IncorrectActivationCode):
            print("Incorrect activation code!", e.reason)
        elif isinstance(e, ActivationCodeExpired):
            print("Activation code has expired!", e.reason)
        else:  # There are more exceptions, but they are not listed here (See the doc of the Me class)
            print("Unknown error!", e.msg, e.reason)
    except MeException as e:
        if isinstance(e, NotValidPhoneNumber):
            print("Not a valid phone number!")
        else:
            print("Unknown error!", e.msg)
    except ValueError as e:
        print("Wrong activation code. It must be a 6-digit number.")

    # If there is no exception, the code will continue here.

.. currentmodule:: meapi.utils.exceptions

====================================================================================================

This are the exceptions that may be raised by the API:

.. autoclass:: MeApiException
.. autoclass:: IncorrectPwdToken
.. autoclass:: NewAccountException
.. autoclass:: UnfinishedRegistration
.. autoclass:: PhoneNumberDoesntExists
.. autoclass:: IncorrectActivationCode
.. autoclass:: BlockedMaxVerifyReached
.. autoclass:: ActivationCodeExpired
.. autoclass:: SearchPassedLimit
.. autoclass:: ProfileViewPassedLimit
.. autoclass:: UserCommentsDisabled
.. autoclass:: UserCommentsPostingIsNotAllowed
.. autoclass:: CommentAlreadyApproved
.. autoclass:: CommentAlreadyIgnored
.. autoclass:: BlockedAccount
.. autoclass:: ForbiddenRequest

====================================================================================================

This are the exceptions that may be raised by the library:

.. autoclass:: MeException
.. autoclass:: NotValidPhoneNumber
.. autoclass:: NotValidAccessToken
.. autoclass:: NotLoggedIn
.. autoclass:: NeedActivationCode
.. autoclass:: ContactHasNoUser
.. autoclass:: FrozenInstance
.. autoclass:: BrokenCredentialsManager
