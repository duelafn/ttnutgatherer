# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
NutgathererApp
app
'''.split()

import os.path
import warnings

from functools import partial

from kivy.config import Config
# Config.set('graphics', 'fullscreen', 'auto')
Config.set('kivy', 'exit_on_escape', 1)

import kivy
kivy.require('1.10.0')

from kivy.clock import Clock
from kivy.factory import Factory
import kivy.core.window
import kivy.uix.screenmanager
import kivy.resources
kivy.resources.resource_add_path(os.path.dirname(__file__))

from amethyst.games import Filter, Grant

import amethyst.ttkvlib.app
import amethyst.ttkvlib.widgets  # Add ttkvlib widgets to the Factory

import ttnutgatherer

class NutgathererApp(amethyst.ttkvlib.app.App):
    XDG_APP = 'nutgatherer'

    game = Factory.ObjectProperty()

    mode = Factory.StringProperty()
    playerno = Factory.NumericProperty()

    def __init__(self):
        super().__init__()
        kivy.core.window.Window.bind(on_key_down=self.on_key_down)
        self.slide_transition = kivy.uix.screenmanager.SlideTransition()
        self.no_transition = kivy.uix.screenmanager.NoTransition()

    def build(self):
        self.root = Factory.FullScreen()
        self.screen = self.root.screen
        self.main = self.root.main
        self.draw_pile = self.main.ids['draw_pile']
        self.discard_pile = self.main.ids['discard_pile']
        self.card_fan = self.main.ids['card_fan']
        self.screen.transition = self.no_transition
        # self.screen.current = 'setup'
        self.screen.current = 'main'
        self.start_game_single(0)
        return self.root

    def start_game_single(self, num_ai):
        self.mode = 'single'
        self.game = ttnutgatherer.Engine(num_players = 1 + num_ai)
        self.playerno = self.game.new_player()
        self.game.observe(self.playerno, self.dispatch_notice)
        # TODO: Add AI Players
        self.game.initialize()
        self.game.call_immediate('begin')
        self.game.process_queue()
        self.screen.current = 'main'

    def draw_cards(self, card_ids, dt=None):
        id = card_ids[0]
        card = self.game.stor_get(id)
        if card:
            for n, c in enumerate(self.card_fan.cards):
                if c['card'].name > card.name:
                    break
            else:
                n = len(self.card_fan)
            widget = self.card_fan.get_card_widget()
            widget.copy_from(self.draw_pile)
            self.card_fan.insert(n, dict(card=card), widget=widget)

        if len(card_ids) > 1:
            Clock.schedule_once(partial(self.draw_cards, card_ids[1:]), 0.100)

    def on_card_press(self, fan, index, data, widget, touch):
        if index in fan.lifted_cards:
            fan.lifted_cards.remove(index)
        else:
            fan.lifted_cards.append(index)


    def on_card_drag(self, fan, index, data, widget, touch):
        # TODO: check current actions, abort unless we are allowed
        # Dragging a single card - let it ride
        if not fan.lifted_cards or fan.lifted_cards == [index]:
            return

        # Dragging multiple cards, this needs to be a stash
        if index not in fan.lifted_cards:
            fan.lifted_cards.append(index)

        # Need 3 cards for a stash
        if 3 != len(fan.lifted_cards):
            return fan.abort_drag(touch)

        # They must all have the same name
        if 1 != len(set(fan[i]['card'].name for i in fan.lifted_cards)):
            return fan.abort_drag(touch)

        # They must all be numbers
        if 'number' not in fan[index]['card'].flags:
            return fan.abort_drag(touch)

        for i in fan.lifted_cards:
            fan.add_to_drag(i, touch)

    def on_card_drop(self, fan, index, data, widget, touch):
        dragged = list(fan.dragged(touch))
        if 3 == len(dragged):
            print("Store")
            # TODO: check that we drop on the stash
            store = self.action('store')
            if store:
                self.trigger(store, cards=[ d['card'].id for idw in dragged ])
                # TODO: remove cards from the hand, add them back in if the store fails

        elif 1 == len(dragged):
            # TODO: depends on where we drop it
            print("Other")
            pass

    def on_notice_call_begin(self, game, player, data):
        Clock.schedule_once(partial(self.draw_cards, data['hand']), 0.500)

    def on_notice_call_start_turn(self, game, player, data):
        pass

    def on_notice_call_draw(self, game, player, data):
        pass

    def on_notice_call_store(self, game, player, data):
        pass

    def on_notice_call_end_turn(self, game, player, data):
        pass


    def action(self, filt=None, **kwargs):
        if kwargs and filt is None:
            filt = Filter(**kwargs)
        elif isinstance(filt, str):
            filt = Filter(name=filt)
        if filt:
            rv = self.game.list_grants(self.playerno, filt)
            if 1 == len(rv):
                return rv[0]
            if 1 < len(rv):
                warnings.warn("Fould multiple matches for grant {}".format(filt))
                return rv[0]
        return None

    def trigger(self, grant, **kwargs):
        if isinstance(grant, Grant):
            grant = grand.id
        self.game.trigger(self.playerno, grant, kwargs)


    def on_key_down(self, win, key, scancode, string, modifiers):
        if key == 292: # F11
            win.fullscreen = 'auto' if win.fullscreen is False else False
            win.update_viewport()
            return True

    def on_stop(self):
        # TODO: Disconnect from server
        super().on_stop()
