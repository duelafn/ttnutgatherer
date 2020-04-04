# -*- coding: utf-8 -*-
"""

"""
# SPDX-License-Identifier: GPL-3.0
__all__ = '''
NutgathererApp
app
'''.split()

import os.path

import kivy
kivy.require('1.10.0')

# from kivy.clock import Clock, mainthread
from kivy.factory import Factory
import kivy.core.window
import kivy.uix.screenmanager
import kivy.resources
kivy.resources.resource_add_path(os.path.dirname(__file__))

import amethyst.ttkvlib.app

import ttnutgatherer

class NutgathererApp(amethyst.ttkvlib.app.App):
    XDG_APP = 'nutgatherer'

    mode = Factory.StringProperty()
    playerno = Factory.NumericProperty()

    hand = Factory.ListProperty()
    storage = Factory.ListProperty()

    def __init__(self):
        super().__init__()
        kivy.core.window.Window.bind(on_key_down=self.on_key_down)
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
        self.game.observe(self.playerno, self.dispatch_notice)
        # TODO: Add AI Players
        self.game.initialize()
        self.game.call_immediate('begin')
        self.game.process_queue()
        self.screen.current = 'main'

    def on_notice_call_begin(self, game, player, data):
        print(data['hand'])
        self.hand = data['hand']

    def on_notice_call_start_turn(self, game, player, data):
        pass

    def on_notice_call_draw(self, game, player, data):
        pass

    def on_notice_call_store(self, game, player, data):
        pass

    def on_notice_call_end_turn(self, game, player, data):
        pass

    def on_key_down(self, win, key, scancode, string, modifiers):
        pass

    def on_stop(self):
        # TODO: Disconnect from server
        super().on_stop()
