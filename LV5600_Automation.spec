# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[('lib/WinInputSimulator.dll', '.'),
                       ('lib/opencv_world480.dll', '.'),
                       ('lib/WaveformImageAnalysisLib.dll', '.'),
                       ],
             datas=[
                    ('gui/resources/LV5600-Automation-GUI.ui', 'resources'),
                    ('gui/resources/Olympus_Corporation_logo.svg.png', 'resources'),
                    ('gui/resources/icon.ico', 'resources'),
                    ('config/config.ini', 'config')],
             hiddenimports=['gui.my_gui_prev'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='LV5600-OCB-Automation-V3.0.1-YCbCr',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True ,
          icon='gui/resources/icon.ico')

# adjust the path to the icon file if necessary
appl = BUNDLE(exe,
              name='main.app',
              icon=None,
              bundle_identifier=None)