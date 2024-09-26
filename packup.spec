# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager', 'D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager\venv\Lib\site-packages'],
    binaries=[],
    datas=[
        ('resource', 'resource'),
        ('data', 'data')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Manager_Executable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Manager_Executable',
    distpath='D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager\output\dist',
    workpath='D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager\output\build'
)
