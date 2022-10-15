# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             binaries=[],
             datas=[('data','data'),('design','design'),('image','image'),('music','music'),('soundfx','soundfx')],
             hiddenimports=['numpy','pygame'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ghcaramel',
          debug=False,
          strip=False,
          upx=True,
          console=True )
