# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for LAN Messenger Server (Console)."""

import os
import sys

spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
project_dir = os.path.dirname(spec_dir)

a = Analysis(
    [os.path.join(project_dir, 'run_server.py')],
    pathex=[os.path.dirname(project_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'messenger.shared.constants',
        'messenger.shared.protocol',
        'messenger.server.server',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LAN_Messenger_Server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console window for server
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_dir, 'app_icon.ico'),
)
