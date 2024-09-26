# -*- mode: python ; coding: utf-8 -*-

import os
import sys


block_cipher = None
NAME = "Rinne Toolkit"
a = Analysis(
    ['main.py', 'utils.py', 'crawler.py'],
    pathex=[r'D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager\venv\Lib\site-packages'],
    #pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['qfluentwidgets', 'keyboard', 'scipy', 'numpy', 'PyQt5', 'bs4', 'requests', 'urllib.request', 'rarfile', 'lxml.etree'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=r'resources\images\avatar.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=NAME,
)
