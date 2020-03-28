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

    def __init__(self):
        global app
        app = self
        ## Items for amethyst.ttlib.App:
        self.register_event_type('on_server_message')
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
        self.screen.current = 'main'
        return self.root

    def on_server_message(self, msg):
        super().on_server_message(msg)

    def on_key_down(self, win, key, scancode, string, modifiers):
        if key == 282:   # F1
            return True  # Block F1 settings editor
        elif key == 292: # F11
            win.fullscreen = 'auto' if win.fullscreen is False else False
            win.update_viewport()
            return True


## Items for amethyst.ttlib.App:

    def on_stop(self):
        self.shutdown()
        super().on_stop()

    def on_shutdown(self, *args):
        self._on_shutdown.append(args)
    def shutdown(self):
        pass
#         for args in self._on_shutdown:
#             try:
#                 if args and callable(args[0]):
#                     args[0](*args[1:])
#                 elif 1 == len(args):
#                     args[0].close()
#                 else:
#                     getattr(args[0], args[1])(*args[2:])
#             except Exception as err:
#                 sys.stderr.write("[ERROR] App.shutdown: {}\n".format(err))

    @classmethod
    def user_conf(cls, *args, **kwargs):
        return utg_common.path.user_conf(cls.XDG_APP, *args, **kwargs)
    @classmethod
    def user_data(cls, *args, **kwargs):
        return utg_common.path.user_data(cls.XDG_APP, *args, **kwargs)
    @classmethod
    def user_cache(cls, *args, **kwargs):
        return utg_common.path.user_cache(cls.XDG_APP, *args, **kwargs)

