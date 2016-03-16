# -*- mode: python -*-


from kivy.tools.packaging.pyinstaller_hooks import (
    hookspath,
    runtime_hooks
)

import sdl2
import glew

block_cipher = None

a = Analysis(['main.py'],
             pathex=['C:\\Users\\Ben\\Documents\\OpenCV_HummingbirdsMotion\\MotionMeerkat'],
             binaries=[],
             datas=None,
             hookspath=hookspath(),
             runtime_hooks=runtime_hooks())
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, 
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='main')
