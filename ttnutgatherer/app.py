# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
NutgathererApp
app
'''.split()

import kivy
kivy.require('1.10.0')

# from kivy.clock import Clock, mainthread
from kivy.factory import Factory
import kivy.app
import kivy.core.window
import kivy.uix.screenmanager

# from amethyst.core.util import cached_property

import ttnutgatherer

app = None
class NutgathererApp(kivy.app.App):
    XDG_APP = 'nutgatherer'
    mode = Factory.StringProperty()
    playerno = Factory.NumericProperty()

    hand = Factory.ListProperty()
    storage = Factory.ListProperty()

    def __init__(self):
        global app
        app = self
        ## Items for amethyst.ttlib.App:
        self.register_event_type('on_server_notice')
        super().__init__()
        kivy.core.window.Window.bind(on_key_down=self.on_key_down)
        ## Back to normal
        self.slide_transition = kivy.uix.screenmanager.SlideTransition()
        self.no_transition = kivy.uix.screenmanager.NoTransition()

    def build(self):
        self.root = Factory.FullScreen()
        self.screen = self.root.screen
        self.main = self.root.main
        self.screen.transition = self.no_transition
        self.screen.current = 'setup'
        return self.root

    def start_game_single(self, num_ai):
        self.mode = 'single'
        self.game = ttnutgatherer.Engine(num_players = 1)# + num_ai)
        self.playerno = self.game.new_player()
        self.game.observe(self.playerno, self.on_server_notice)
        # TODO: Add AI Players
        self.game.call_immediate('begin')
        self.screen.current = 'main'

    def on_notice_call_begin(self, data):
        self.hand = data['hand']

    def on_notice_call_start_turn(self, data):
        pass

    def on_notice_call_draw(self, data):
        pass

    def on_notice_call_store(self, data):
        pass

    def on_notice_call_end_turn(self, data):
        pass

    def on_server_notice(self, game, seq, player, notice):
        # This should be handled by Client(): it gives me a configured game
        if self.mode != 'single':
            self.game
        if notice.type == NoticeType.CALL:
            cb = self.getattr(self, f"on_notice_call_{notice.name}", None)
            if cb and callable(cb):
                cb(notice.data)

    def on_key_down(self, win, key, scancode, string, modifiers):
        pass

    def on_stop(self):
        # TODO: Disconnect from server
        super().on_stop()
