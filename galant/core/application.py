# -*- coding: utf-8 -*-

from .types_ import Scope, Receive, Send


class Galant(object):
    def __init__(self):
        pass

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        pass
