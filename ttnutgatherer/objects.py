# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
Card
'''.split()

from amethyst.core import Attr
from amethyst.games import Filterable
from amethyst.games.objects import Pile

class Card(Filterable):
    pass

class Player(Filterable):
    hand = Attr(default=Pile)
    storage = Attr(default=Pile)
