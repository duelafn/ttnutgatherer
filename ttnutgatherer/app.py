# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
NutgathererApp
app
'''.split()

from functools import partial
import math
import os.path

from kivy.config import Config
# Config.set('graphics', 'fullscreen', 'auto')
Config.set('kivy', 'exit_on_escape', 1)

import kivy
kivy.require('1.10.0')

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import inch
import kivy.core.window
import kivy.resources
import kivy.uix.screenmanager
kivy.resources.resource_add_path(os.path.dirname(__file__))

from amethyst.games import Filter, Grant, NoticeType
from amethyst.ttkvlib.behaviors.toast import ToastBehavior
from amethyst.ttkvlib.util import rotation_for_animation
import amethyst.ttkvlib.app
import amethyst.ttkvlib.widgets  # Add ttkvlib widgets to the Factory

import ttnutgatherer

GRANTS = dict(
    draw     = (10, "Draw a card"),
    store    = (20, "Store 3 matching cards"),
    discard  = (70, "Discard"),
    end_turn = (90, "End turn"),
)

class NutgathererApp(ToastBehavior, amethyst.ttkvlib.app.App):
    XDG_APP = 'nutgatherer'

    game = Factory.ObjectProperty()
    notes = Factory.StringProperty()

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
        Clock.schedule_interval(lambda *args: self.game.process_queue(), 0)
        self.screen.current = 'main'

    def draw_card(self):
        self.trigger('draw')

    def on_card_press(self, fan, index, data, widget, touch):
        if touch.is_double_tap:
            print("Store", data['card'].name)
            return

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
            store = self.get_action('store')
            if store:
                self.trigger(store, cards=[ d['card'].id for i, d, w in dragged ])
                # TODO: remove cards from the hand, add them back in if the store fails

        elif 0 == len(dragged) or (1 == len(dragged) and data['card'].id == dragged[0][2].id):
            card = data['card']
            if self.discard_pile.collide_point(*touch.pos):
                if self.trigger('discard', card=card.id):
                    self.discard_anim(fan, index, data, widget)
            else:
                print("Other")


    def on_notice_call_begin(self, game, player, data):
        if player == self.playerno:
            Clock.schedule_once(partial(self.draw_cards_anim, data['hand']), 0.500)

    def on_notice_call_start_turn(self, game, player, data):
        print("Start turn", data)

    def on_notice_call_draw(self, game, player, data):
        if player == self.playerno and data['drawn']:
            self.draw_cards_anim( [data['drawn']] )

    def on_notice_call_store(self, game, player, data):
        print("Store", data)

    def on_notice_call_end_turn(self, game, player, data):
        print("End turn", data)



    def dispatch_notice(self, game, seq, player, notice):
        super(NutgathererApp,self).dispatch_notice(game, seq, player, notice)
        if notice.type in (NoticeType.GRANT, NoticeType.EXPIRE):
            self.check_notes()
        if notice.type == NoticeType.EXPIRE:
            print(notice)

    def check_notes(self):
        self.notes = "Available actions:\n" + "".join(f"  * {x[1]}\n" for x in sorted(
            GRANTS.get(g.name, (0, g.name)) for g in self.game.list_grants(self.playerno)
        ))


    def discard_anim(self, fan, index, data, widget):
        pile = self.discard_pile
        if fan and index is not None:
            fan.pop(index, recycle=False)
        dt = math.hypot(widget.x-pile.x, widget.y-pile.y) / (fan.linear_speed if fan else inch(15))
        anim = Factory.Animation(
            x=pile.x, y=pile.y,
            width=pile.width, height=pile.height,
            rotation=rotation_for_animation(widget.rotation, 0),
            duration=min(2,dt),
        )
        anim.bind(on_complete=lambda *args: self.discard_complete(fan, data['card'], widget))
        anim.start(widget)

    def discard_complete(self, fan, card, widget):
        if fan:
            fan.recycle(widget)
        self.discard_pile.card = card
        self.discard_pile.show_front = True

    def draw_cards_anim(self, card_ids, dt=None):
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
            Clock.schedule_once(partial(self.draw_cards_anim, card_ids[1:]), 0.100)


    def get_action(self, filt=None, **kwargs):
        if kwargs and filt is None:
            filt = Filter(**kwargs)
        elif isinstance(filt, str):
            grant = self.game.find_grant(self.playerno, filt)
            if grant:
                return grant
            filt = Filter(name=filt)
        if filt:
            rv = self.game.list_grants(self.playerno, filt)
            if 1 == len(rv):
                return rv[0]
            if 1 < len(rv):
                self.error(f"Multiple '{GRANTS.get(grant, (0, grant))[1]}' actions - that was not expected")
                return rv[0]
        return None

    def trigger(self, grant, **kwargs):
        if isinstance(grant, str):
            gr = self.get_action(grant)
            if gr:
                grant = gr.id
            else:
                self.warning(f"Not allowed to '{GRANTS.get(grant, (0, grant))[1]}' at this time", 1.5)
                return False
        if isinstance(grant, Grant):
            grant = grant.id
        return self.game.trigger(self.playerno, grant, kwargs)

    def on_key_down(self, win, key, scancode, string, modifiers):
        if key == 292: # F11
            win.fullscreen = 'auto' if win.fullscreen is False else False
            win.update_viewport()
            return True

    def on_stop(self):
        # TODO: Disconnect from server
        super().on_stop()
