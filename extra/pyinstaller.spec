#!/usr/bin/pyinstaller --workpath /tmp
# -*- mode: python -*-
from kivy.deps import sdl2, glew

block_cipher = None

a = Analysis(
    ['nutgatherer'],
    pathex                  = ['Z:\\src'],
    binaries                = [],
    datas                   = [],
    hiddenimports           = [
        'win32timezone', # something in kivy imports this dynamically
    ],
    hookspath               = [],
    runtime_hooks           = [],
    excludes                = [],
    win_no_prefer_redirects = False,
    win_private_assemblies  = False,
    cipher                  = block_cipher,
    noarchive               = False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts, a.binaries, a.zipfiles, a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)], # added
    name                      = 'test',
    debug                     = False,
    bootloader_ignore_signals = False,
    strip                     = False, # unchanged (not recommended for Windows)
    upx                       = False, # changed - run on host: upx motionforce/MotionForce.exe
    runtime_tmpdir            = None,
    console                   = False, # changed
)
