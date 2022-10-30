# -*- coding: utf-8 -*-
"""
context副本, 实现flask中的全局request

g可以被request.state替代, 是否考虑引入?
添加background task替代存储在response?
"""
import typing as t
import contextvars

# LocalProxy内部实现?
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .http.request import Request

_cv_request = contextvars.ContextVar("galant.request_ctx")
request: "Request" = LocalProxy(_cv_request)  # noqa
