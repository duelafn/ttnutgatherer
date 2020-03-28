# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
Engine
'''.split()


from amethyst.core import Attr
from amethyst.games import action
from amethyst.games.plugins import GrantManager, Turns
import amethyst.games

from .objects import Card


class Engine(amethyst.games.Engine):
    draw_pile = Attr(default=Pile)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_plugin(GrantManager())
        self.register_plugin(Turns(setup_rounds=1))
        self.register_plugin(BaseGame())

    def initialize()
        self.draw_pile.extend([ Card(name="1", flags=set(("acorn", "number",))) for i in range(30) ])


class BaseGame(amethyst.games.EnginePlugin):
    AMETHYST_PLUGIN_COMPAT = 1  # Plugin API version

    @action
    def begin(self, game, stash):
        game.call_immediate('start_turn')

    @action
    def start_turn(self, game, stash):
        game.turn_start()
        game.grant(game.turn_player_num(), Grant(name="end_turn"))



    @action
    def end_turn(self, game, stash):
        game.commit()
        game.call_immediate('start_turn')
