# -*- coding: utf-8 -*-
"""
Add Simplified Chinese support to the Z-Anatomy Startup.blend.

What it does:
  1. Replaces the embedded 'Translations' text block with a 6-column CSV
     (English;Latin;Français;Español;Portugues;中國人).
  2. Loads a CJK font into the .blend as a datablock named 'ZhFont'
     (the name the updated __init__.py maps '中國人' to).
  3. Optionally replaces the embedded 'z-anatomy.py' text block with the
     updated __init__.py so the template runs the new code.
  4. Saves the .blend.

Usage (from the folder containing Startup.blend):
  blender --background Startup.blend --python add_chinese_translation.py -- \
      --csv Translations_CN.csv --init __init__.py --out Startup.blend

All arguments are optional; sensible defaults are used. Run from the folder
that contains Startup.blend, or pass absolute paths.
"""
import bpy
import os
import sys
import argparse

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
HERE = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Add Simplified Chinese to Z-Anatomy Startup.blend')
parser.add_argument('--csv', default=os.path.join(HERE, 'Translations_CN.csv'),
                    help='6-column translation table (default: Translations_CN.csv next to this script)')
parser.add_argument('--font', default='',
                    help='CJK font file to embed (default: first match from a built-in search list)')
parser.add_argument('--init', default='',
                    help='updated __init__.py to embed as the z-anatomy.py text block')
parser.add_argument('--out', default='',
                    help='output .blend path (default: overwrite the loaded file)')
args = parser.parse_args(argv)

# ---------------------------------------------------------------- 1. CSV ----
with open(args.csv, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
header = lines[0].split(';')
assert len(header) == 6 and header[-1] == '中國人', \
    'unexpected CSV header: %r (expected 6 columns ending with 中國人)' % (header,)

txt = bpy.data.texts.get('Translations')
if txt is None:
    txt = bpy.data.texts.new('Translations')
    print('[patch] WARNING: no Translations text block found; created a new one')
txt.clear()
txt.write(content)
print('[patch] Translations now holds %d rows' % len(lines))

# --------------------------------------------------------------- 2. font ----
CANDIDATES = [args.font] + [
    # Windows
    r'C:\Windows\Fonts\msyh.ttc',       # Microsoft YaHei
    r'C:\Windows\Fonts\msyh.ttf',
    r'C:\Windows\Fonts\simhei.ttf',     # SimHei
    r'C:\Windows\Fonts\simsun.ttc',     # SimSun
    r'C:\Windows\Fonts\Deng.ttf',       # DengXian
    # macOS
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    # Linux
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/truetype/arphic/uming.ttc',
]

font = bpy.data.fonts.get('ZhFont')
if font is not None:
    print('[patch] ZhFont already present, reusing it')
else:
    for path in CANDIDATES:
        if path and os.path.isfile(path):
            font = bpy.data.fonts.load(path, check_existing=True)
            print('[patch] loaded font %s (datablock %r)' % (path, font.name))
            break
    assert font is not None, \
        'no CJK font found; pass one explicitly with --font /path/to/font.ttc'
    font.name = 'ZhFont'
font.use_fake_user = True
print('[patch] font datablock ZhFont ready (fake_user=%s)' % font.use_fake_user)

# ------------------------------------------------------- 3. embedded code ----
if args.init and os.path.isfile(args.init):
    with open(args.init, 'r', encoding='utf-8') as f:
        code = f.read()
    code_txt = bpy.data.texts.get('z-anatomy.py')
    if code_txt is None:
        code_txt = bpy.data.texts.new('z-anatomy.py')
        print('[patch] WARNING: no z-anatomy.py text block found; created one')
    code_txt.clear()
    code_txt.write(code)
    print('[patch] embedded z-anatomy.py replaced with %s' % args.init)

# --------------------------------------------------------------- 4. save ----
out = args.out or bpy.data.filepath
bpy.ops.wm.save_as_mainfile(filepath=out, check_existing=False)
print('[patch] saved: %s' % out)
