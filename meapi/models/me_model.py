import inspect
import json
from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Union, List, Dict, Type
from datetime import datetime, date
from meapi.utils.exceptions import FrozenInstance
from logging import getLogger
if TYPE_CHECKING:  # always False at runtime.
    from meapi import Me

IGNORED_KEYS = []
_logger = getLogger(__name__)


class _ParameterReader(ABCMeta):
    """Internal class to get class init parameters"""
    def __init__(cls, *args, **kwargs):
        parameters = inspect.signature(cls.__init__).parameters
        parameters = {key: value for key, value in parameters.items() if key not in ['self', 'args', 'kwargs']}
        try:
            cls._init_parameters = cls.__bases__[0]._init_parameters.copy()
            cls._init_parameters.update(parameters)
        except AttributeError:
            cls._init_parameters = parameters

        super().__init__(*args, **kwargs)


class MeModel(metaclass=_ParameterReader):
    """
    Base class for all models.
        - Allow instances to be comparable, subscript, hashable, immutable (In some cases), and json serializable.

    Examples:

        >>> my_profile = me.get_my_profile() # Get your profile.
        >>> my_profile.name # regular access
        >>> my_profile['name'] # subscript access
        >>> my_profile.get('name', default='') # safe access
        >>> my_profile.as_dict() # get all data as dict
        >>> my_profile.as_json() # get all data as json string
        >>> my_profile == other_profile # compare two objects

    Methods:

    .. automethod:: as_dict
    .. automethod:: as_json
    .. automethod:: get
    """
    def __init__(self):
        """
        Add the ``init_done`` flag to the class to prevent attr changes after the init.
        """
        self.__init_done = True

    def as_dict(
            self,
            only: Union[str, List[str]] = None,
            exclude: Union[str, List[str]] = None,
            recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Return class data as ``dict``.

        Examples
        --------
        >>> my_profile = me.get_my_profile() # Get your profile.
        >>> my_profile.as_dict()
        {'phone_number': 972123456789, 'first_name': 'David', 'last_name': 'Lev', 'socials': {'lin ...}
        >>> my_profile.as_dict(only=('phone_number', 'first_name'), recursive=False)
        {'phone_number': 972123456789, 'first_name': 'David'}

        :param only: Return only the given keys.
        :type only: ``str`` | ``list[str]``
        :param exclude: Exclude the given keys.
        :type exclude: ``str`` | ``list[str]``
        :param recursive: If ``True`` (default), return all nested objects as dict.
        :type recursive: ``bool``
        """
        if isinstance(only, str):
            only = (only,)
        if isinstance(exclude, str):
            exclude = (exclude,)
        data = {}
        for (key, value) in self.__dict__.items():
            if str(key).startswith("_") \
                    or (only and key not in only) \
                    or (exclude and key in exclude):
                continue
            if isinstance(value, (str, int, float, bool, dict)):
                data[key] = value
            elif isinstance(value, (list, tuple, set)):
                data[key] = []
                for item in value:
                    if isinstance(item, (str, int, float, bool, dict)):
                        data[key].append(item)
                    elif getattr(item, 'as_dict', None) and recursive:
                        data[key].append(item.as_dict())
            elif getattr(value, 'as_dict', None) and recursive:
                data[key] = getattr(self, key).as_dict()
            elif isinstance(value, (date, datetime)):
                data[key] = str(value)
        return data

    def as_json(
            self,
            only: Union[str, List[str]] = None,
            exclude: Union[str, List[str]] = None,
            recursive: bool = True,
            ensure_ascii: bool = False,
    ) -> str:
        """
        Return class data in ``json`` format.

        :param only: Return only the given keys.
        :type only: ``str`` | ``list[str]``
        :param exclude: Exclude the given keys.
        :type exclude: ``str`` | ``list[str]``
        :param recursive: If ``True`` (default), return all nested objects as dict.
        :type recursive: ``bool``
        :param ensure_ascii: If ``True``, all non-ASCII characters in the output are escaped with ``\\uXXXX`` sequences.
        :type ensure_ascii: ``bool``
        """
        return json.dumps(self.as_dict(
            only=only, exclude=exclude, recursive=recursive
        ), ensure_ascii=ensure_ascii, sort_keys=True, indent=4).encode('utf8').decode()

    @classmethod
    def new_from_dict(cls, data: dict, _client: 'Me' = None, **kwargs):
        """
        Create new instance from dict.
        """
        if not data or data is None:
            return None
        cls_attrs = cls._init_parameters.keys()
        if '_client' in cls_attrs:
            data['_client'] = _client
        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val
        global IGNORED_KEYS
        for key in json_data.copy():
            if key not in cls_attrs:
                if key not in IGNORED_KEYS and not key.startswith('_'):
                    IGNORED_KEYS.append(key)
                    _logger.debug(
                        f"- {cls.__name__}: The key '{key}' with the value of '{json_data[key]}' just skipped. "
                        f"Try to update meapi to the latest version (pip3 install -U meapi) "
                        f"If it's still skipping, open issue in github: <https://github.com/david-lev/meapi/issues>"
                        )
                del json_data[key]
        c = cls(**json_data)
        return c

    def __getitem__(self, item):
        """
        Return the value of the attribute with the given name.

        Example:
            >>> my_profile = me.get_my_profile() # Get your profile.
            >>> my_profile['phone_number']
        """

        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def __setitem__(self, key: str, value: Any):
        """
        Set the value of the attribute with the given name.
            - Example: ``obj['id'] = 123``
        """
        setattr(self, key, value)

    def get(self, item: str, default: Any = None):
        """
        Return the value of the attribute with the given name.
            - Example:
                >>> my_profile = me.get_my_profile() # Get your profile.
                >>> my_profile.get('phone_number')

        Parameters:
            item (``str``):
                The name of the attribute.
            default (``any``):
                The default value to return if the attribute does not exist.
                    - Default: ``None``

        Returns:
            The value of the attribute, or ``default`` if the attribute does not exist.
        """
        return getattr(self, item, default)

    def __setattr__(self, key: str, value: Any):
        """
        Prevent attr changes after the init in protected data classes
        """
        if getattr(self, '_MeModel__init_done', None):
            raise FrozenInstance(self, key)
        return super().__setattr__(key, value)

    def __str__(self) -> str:
        """
        Return class data in json format
        """
        return self.as_json()

    def __repr__(self):
        """Return a string representation of the object in ``ClassName(attr1='Test', attr2=123)`` format."""
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.as_dict().items())})"

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        Raises:
            TypeError: If the object is not hashable (if it has no ``phone_number``, ``uuid``, or ``id`` attribute).
        """
        if hasattr(self, 'phone_number'):
            return hash(self.phone_number)
        elif hasattr(self, 'uuid'):
            return hash(self.uuid)
        elif hasattr(self, 'id'):
            return hash(self.id)
        else:
            raise TypeError(f"Can't hash {self.__class__.__name__} object")

    def __eq__(self, other: Type['MeModel']) -> bool:
        """
        Return ``True`` if the two objects are equal.
        """
        if not isinstance(other, self.__class__):
            return False
        return other and self.__hash__() == other.__hash__()

    def __ne__(self, other: Type['MeModel']) -> bool:
        """
        Return ``True`` if the two objects are not equal.
        """
        return not self.__eq__(other)
