# -*- coding: utf-8 -*-
import typing as t
import http.cookies

_http_cookie_unquote = http.cookies._unquote  # noqa


def parse_cookie(cookie_string: str) -> t.Dict[str, str]:
    """将cookie字符串解析成dict类型"""
    cookie_dict = {}

    for item in cookie_string.split(";"):
        if "=" in item:
            name, value = item.split("=", 1)
        else:
            # 有可能会没有name
            # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
            name, value = "", item

        name, value = name.strip(), value.strip()
        if value or name:
            # http.cookies._unquote是Python实现, 是否更换成C实现?
            cookie_dict[name] = _http_cookie_unquote(value)
    return cookie_dict
