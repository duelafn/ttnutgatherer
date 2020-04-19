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

from ttnutgatherer.objects import Card, Player


class Engine(amethyst.games.Engine):
    draw_pile = Attr(default=Pile)
    discard_pile = Attr(default=Pile)
    num_players = Attr(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_plugin(GrantManager())
        self.register_plugin(Turns())
        self.register_plugin(ObjectStore())
        self.register_plugin(BaseGame())

    # Some shortcut methods and properties:
    def new_player(self):
        return self.set_random_player(Player(), self.num_players)
    def grant_current(self, *args, **kwargs):
        return self.grant(self.turn_player_num(), Grant(*args, **kwargs))
    @property
    def player(self):
        return self.turn_player()

    def initialize(self):
        super().initialize()
        cards = [ ]
        cards.extend([ Card(name="1", flags=set(("acorn", "number",))) for i in range(30) ])
        cards.extend([ Card(name="2", flags=set(("acorn", "number",))) for i in range(24) ])
        cards.extend([ Card(name="3", flags=set(("acorn", "number",))) for i in range(18) ])
        cards.extend([ Card(name="4", flags=set(("acorn", "number",))) for i in range(12) ])
        cards.extend([ Card(name="5", flags=set(("acorn", "number",))) for i in range(9) ])

        cards.extend([ Card(name="quarrel",   flags=set(("action",))) for i in range(8) ])
        cards.extend([ Card(name="hoard",     flags=set(("action",))) for i in range(8) ])
        cards.extend([ Card(name="ambush",    flags=set(("action",))) for i in range(6) ])
        cards.extend([ Card(name="whirlwind", flags=set(("action",))) for i in range(2) ])

        cards.append(Card(name="golden", flags=set(("acorn",))))
        cards.append(Card(name="rotten", flags=set(("acorn",))))
        cards.append(Card(name="winter", flags=set(("action",))))

        self.stor_extend_shared(cards)
        self.draw_pile.extend(card.id for card in cards)



class BaseGame(amethyst.games.EnginePlugin):
    AMETHYST_PLUGIN_COMPAT = 1  # Plugin API version
    drawn_this_turn = Attr(bool)

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

        if reshuffle:
            game.draw_pile.extend(discard)
            game.draw_pile.shuffle()
        else:
            game.discard_pile.extend(discard)


    @action
    def begin(self, game, stash, player_num=None, hand=None):
        if game.is_server():
            self.initial_deal(game)
        elif player_num and hand:
            game.players[player_num].hand.extend(hand)
        game.schedule('start_turn')

    @begin.notify
    def begin(self, game, stash, player_num, kwargs):
        if player_num is not None:
            kwargs['player_num'] = player_num
            kwargs['hand'] = list(game.players[player_num].hand)
        return kwargs


    @action
    def start_turn(self, game, stash):
        game.turn_start()
        self.drawn_this_turn = False
        # Grant a draw action, but do not allow the client to tell us what
        # they drew. In this simple game, the forced kwarg is not necessary
        # (we unconditionally overwrite the `drawn` parameter below), but
        # forcing may be useful in more advanced games. NOTE: The forced
        # parameter is not secret - all players will see it. Use a local
        # dictionary with random keys if you need to keep a secret forced
        # parameter.
        game.grant_current(name="draw", kwargs=dict(drawn=None))

    @action
    def draw(self, game, stash, player_num, drawn=None):
        # When we draw from the server, we actually take the next card off
        # the deck. The client, however, takes the card received from the
        # server's notification (see draw.notify below).
        #
        # Notice that the server overwrites anything the client may have
        # sent in `drawn` (even though we also forced drawn=None in the grant).
        if game.is_server():
            drawn = game.draw_pile.pop()

        # Save the drawn card for notification later
        stash['drawn'] = drawn

        # OPTIONAL: The local game doesn't care about the draw pile since
        # it isn't really used. We could, however, keep it up to date if
        # our game required it:
        ### if drawn is not None: game.draw_pile.stack.remove(drawn)

        # Save the drawn card to the current player's hand
        if drawn is not None:
            game.player.hand.append(drawn)

        # After drawing, what can we do?
        if not self.drawn_this_turn:
            self.drawn_this_turn = True
            game.grant_current(name="end_turn")
        if len(game.player.hand) < 7:
            game.grant_current(name="draw", kwargs=dict(drawn=None))

    @draw.check
    def draw(self, game, stash, player_num, drawn=None):
        return len(game.player.hand) < 7 or not self.drawn_this_turn

    @draw.notify
    def draw(self, game, stash, player_num, kwargs):
        # Send the card drawn only to the current player
        if player_num == game.turn_player_num():
            kwargs['drawn'] = stash['drawn']

    @action
    def store(self, game, stash, player_num, cards):
        print(stash['hand_objs'])

    @store.check
    def store(self, game, stash, player_num, cards):
        if 3 != len(cards):
            return False
        objs = game.player.hand.find(Filter(id=set(cards)))
        if 3 != len(objs):
            return False
        stash['hand_objs'] = objs
        return True


    @action
    def end_turn(self, game, stash, player_num, discard):
        game.commit()
        game.call_immediate('start_turn')
