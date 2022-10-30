# -*- coding: utf-8 -*-
import asyncio
import typing as t
import functools


class cached_property(object):  # noqa
    """与标注库比无锁, 同django.functional.cached_property"""
    __slots__ = ("name", "func")

    name: str

    def __init__(self, func: t.Callable[[t.Any], t.Any]):
        self.func = func

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        rv = self.func(instance)
        instance.__dict__[self.name] = rv
        return rv
