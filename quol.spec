# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/res', 'res'),
        ('app/transitions', 'transitions'),
        ('app/lib', 'lib')
    ],
    hiddenimports=['ollama', 'markdown', 'pygments', 'httpx', 'qasync.asyncSlot', 'pynput', 'PySide6.QtOpenGLWidgets', 'PySide6.QtOpenGL', 'OpenGL.GL', 'seleniumbase', 'selenium', 'selenium.webdriver.support.expected_conditions'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'doctest',
        'xmlrpc',

        'pygments.formatters.bbcode',
        'pygments.formatters.img',
        'pygments.formatters.latex',
        'pygments.formatters.other',
        'pygments.formatters.rtf',
        'pygments.formatters.svg',
        'pygments.styles.abap',
        'pygments.styles.algol',
        'pygments.styles.friendly_grayscale',
        'pygments.styles.native',

        'markdown.extensions.abbr',
        'markdown.extensions.admonition',
        'markdown.extensions.footnotes',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Quol',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_dir='C:/Users/leoch/Downloads/upx-5.0.1-win64/upx-5.0.1-win64',
    upx_exclude=['vcruntime140.dll', 'python*.dll', 'Quol.exe'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app/res/icons/icon.ico'],
)
