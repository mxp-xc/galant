# -*- coding: utf-8 -*-
import typing as t
from urllib.parse import parse_qs

from galant.utils.datastructures import State, MultiValueMapping
from galant.utils.functional import cached_property
from galant.utils.request import parse_cookie
from galant.core.types_ import Scope, Send, Receive


class ClientDisconnect(Exception):
    pass


class Headers(t.Mapping[str, str]):
    __slots__ = ("_data",)
    _data: t.Dict[
        str,
        t.Union[str, t.List[str]]
    ]

    def __init__(
            self,
            raw_headers: t.Iterator[t.Tuple[bytes, bytes]]
    ):
        data = {}
        for key, value in raw_headers:
            key, value = key.lower().decode(), value.decode()

            if key in data:
                v = data[key]
                if isinstance(v, list):
                    v.append(value)
                else:
                    data[key] = [v, value]
            else:
                data[key] = value

        self._data = data

    def get(self, key: str, default=None) -> t.Any:
        try:
            return self[key]
        except KeyError:
            return default

    def getlist(self, key: str) -> t.List[str]:
        value = self._data[key.lower()]
        if isinstance(value, str):
            return [value]
        return value

    def __getitem__(self, key: str) -> str:
        value = self._data[key.lower()]
        if isinstance(value, list):
            return value[0]
        return value

    def __repr__(self):
        return f"Headers({self._data})"

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


class QueryDict(MultiValueMapping):
    __slots__ = ("_data",)

    def __init__(self, query_string: t.Union[str, bytes]):
        if isinstance(query_string, bytes):
            query_string = query_string.decode()
        super().__init__(parse_qs(query_string))

    def __repr__(self):
        return f"QueryDict({self._data})"


class HttpConnection(object):
    def __init__(self, scope: Scope):
        self.scope = scope

    def __getitem__(self, key):
        return self.scope[key]

    @cached_property
    def state(self):
        state = self.scope.setdefault("state", {})
        return State(state)

    @cached_property
    def headers(self) -> Headers:
        return Headers(self.scope["headers"])

    @cached_property
    def query(self) -> QueryDict:
        return QueryDict(self.scope["query_string"])

    @cached_property
    def cookies(self) -> dict:
        cookie_string = self.headers.get("cookie")
        if cookie_string:
            return parse_cookie(cookie_string)
        return {}


class Request(HttpConnection):
    _body: bytes

    def __init__(
            self,
            scope: Scope,
            receive: Receive,
            send: Send
    ):
        super().__init__(scope)
        self._receive = receive
        self._send = send
        self._stream_consumed = False
        self._is_disconnected = False

    @property
    def receive(self):
        return self._receive

    @property
    def send(self):
        return self._send

    @property
    def method(self) -> str:
        return self.scope["method"]

    async def stream(self):
        if self._stream_consumed:
            raise RuntimeError("stream consumed")

        self._stream_consumed = True
        while True:
            message = await self._receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    yield body
                if not message.get("more_body", False):
                    return
            else:  # "http.disconnect"
                self._is_disconnected = True
                raise ClientDisconnect()

    async def body(self):
        if hasattr(self, "_body"):
            return self._body

        chunk = []
        async for data in self.stream():
            chunk.append(data)

        self._body = b"".join(chunk)
        return self._body
