# -*- mode: python ; coding: utf-8 -*-

a2 = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/lib', 'lib')],
    hiddenimports=[
        'ollama',
        'markdown',
        'pygments',
        'httpx',
        'pynput',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'selenium.webdriver.support.wait',
        'seleniumbase',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'doctest',
        'xmlrpc',
        'lxml',
        'html5lib',

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

pyz2 = PYZ(a2.pure)
exe2 = EXE(
    pyz2,
    a2.scripts,
    [],
    exclude_binaries=True,
    name='Quol',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=['app/res/icons/icon.ico'],
)

coll = COLLECT(
    exe2,
    a2.binaries,
    a2.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Quol',
)

