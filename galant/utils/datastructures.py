# -*- coding: utf-8 -*-

import typing as t


class CaseInsensitiveMapping(t.Mapping[str, t.Any]):
    """大小写不敏感的映射"""
    __slots__ = ("_data",)

    def __init__(self, data):
        self._data = {key.lower(): value for key, value in data.items()}

    def __getitem__(self, key):
        return self._data[key.lower()]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return (key for key, _ in self._data.values())

    def __repr__(self):
        return repr(self._data)


class State(object):
    """存储数据类型
    代理一个dict, 使用访问属性的方式替代dict使用方式
    """
    __slots__ = ("_state",)
    _state: t.Dict[str, t.Any]

    def __init__(self, state=None):
        object.__setattr__(self, "_state", state or {})

    def __getattr__(self, key):
        try:
            return self._state[key]
        except KeyError:
            msg = f"'{self.__class__.__name__}' object has no attribute '{key}'"
            raise AttributeError(msg)

    def __setattr__(self, key, value):
        self._state[key] = value

    def __delattr__(self, key):
        del self._state[key]


class MultiValueMapping(t.Mapping[str, t.List[str]]):
    __slots__ = ("_data",)

    def __init__(self, data: t.Mapping[str, t.List[str]]):
        self._data = data

    def getlist(self, key) -> t.List[str]:
        return self._data[key]

    def __getitem__(self, key) -> str:
        return self._data[key][0]

    def __iter__(self) -> t.Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key):
        return key in self._data

    def keys(self) -> t.KeysView[str]:
        return self._data.keys()

    def values(self) -> t.ValuesView[t.List[str]]:
        return self._data.values()

    def items(self) -> t.ItemsView[str, t.List[str]]:
        return self._data.items()
