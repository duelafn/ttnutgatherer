# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
Engine
'''.split()


from amethyst.core import Attr
from amethyst.games import action
from amethyst.games.plugins import GrantManager, Turns, ObjectStore, Grant
from amethyst.games.objects import Pile
import amethyst.games

from .objects import Card, Player


class Engine(amethyst.games.Engine):
    draw_pile = Attr(default=Pile)
    discard_pile = Attr(default=Pile)
    num_players = Attr(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_plugin(GrantManager())
        self.register_plugin(Turns(setup_rounds=1))
        self.register_plugin(ObjectStore())
        self.register_plugin(BaseGame())

    def new_player(self):
        return self.set_random_player(Player(), self.num_players)

    def initialize(self):
        super().initialize()
        cards = [ ]
        cards.extend([ Card(name="1", flags=set(("acorn", "number",))) for i in range(30) ])
        cards.extend([ Card(name="2", flags=set(("acorn", "number",))) for i in range(24) ])
        cards.extend([ Card(name="3", flags=set(("acorn", "number",))) for i in range(18) ])
        cards.extend([ Card(name="4", flags=set(("acorn", "number",))) for i in range(12) ])
        cards.extend([ Card(name="5", flags=set(("acorn", "number",))) for i in range(9) ])

        cards.extend([ Card(name="Quarrel",   flags=set(("action",))) for i in range(8) ])
        cards.extend([ Card(name="Hoard",     flags=set(("action",))) for i in range(8) ])
        cards.extend([ Card(name="Ambush",    flags=set(("action",))) for i in range(6) ])
        cards.extend([ Card(name="Whirlwind", flags=set(("action",))) for i in range(2) ])

        cards.append(Card(name="Golden Acorn", flags=set(("acorn",))))
        cards.append(Card(name="Rotten Acorn", flags=set(("acorn",))))
        cards.append(Card(name="Winter", flags=set(("action",))))

        self.stor_extend_shared(cards)
        self.draw_pile.extend(card.id for card in cards)



class BaseGame(amethyst.games.EnginePlugin):
    AMETHYST_PLUGIN_COMPAT = 1  # Plugin API version
    drawn_this_turn = Attr(int)

    def initial_deal(self, game):
        game.draw_pile.shuffle()
        reshuffle = False
        discard = []
        for p in game.players:
            while len(p.hand) < 7:
                card_id = game.draw_pile.pop()
                card = game.stor_get(card_id)
                if 'action' in card.flags:
                    if card.name == "Winter":
                        reshuffle = True
                    discard.append(card_id)
                else:
                    p.hand.append(card_id)


    @action
    def begin(self, game, stash):
        game.call_immediate('start_turn')
    @begin.notify
    def begin(self, game, stash, player_num, kwargs):
        kwargs['hand'] = list(game.players[player_num].hand)

    @action
    def start_turn(self, game, stash):
        game.turn_start()
        self.drawn_this_turn = 0
        game.grant(game.turn_player_num(), Grant(name="draw"))

    @action
    def draw(self, game, stash):
        card_id = game.draw_pile.pop()
        game.grant(game.turn_player_num(), Grant(name="draw"))
        game.grant(game.turn_player_num(), Grant(name="end_turn"))
    @draw.check
    def draw(self, game, stash):
        pass

    @action
    def store(self, game, stash):
        pass


    @action
    def end_turn(self, game, stash, *, discard):
        game.commit()
        game.call_immediate('start_turn')
