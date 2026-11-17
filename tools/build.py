"""Build index.html (a published Twine 2 / Harlowe 3.3.9 story) from source.twee.

Run from anywhere:  python3 -I tools/build.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'tools', 'harlowe-3.3.9-template.html')
SOURCE = os.path.join(ROOT, 'source.twee')
OUTPUT = os.path.join(ROOT, 'index.html')
DESCRIPTION = 'A funny Twine choose-your-own-adventure: help Gru stop Dr. Snoozemonger from stealing every banana on Earth.'

HEADER = re.compile(r'^:: (?P<name>.+?)(?: \[(?P<tags>[^\]]*)\])?(?: (?P<meta>\{.*\}))?\s*$')


def parse_twee(src):
    """Return [{'name', 'tags', 'meta', 'text'}] in file order (Twee 3)."""
    passages, cur = [], None
    for line in src.split('\n'):
        m = HEADER.match(line) if line.startswith(':: ') else None
        if m:
            cur = {'name': m.group('name').strip(),
                   'tags': (m.group('tags') or '').split(),
                   'meta': json.loads(m.group('meta')) if m.group('meta') else {},
                   'lines': []}
            passages.append(cur)
        elif cur is not None:
            cur['lines'].append(line)
    for p in passages:
        p['text'] = '\n'.join(p.pop('lines')).strip('\n')
    return passages


def esc(s):
    return html.escape(s, quote=True)


def build():
    passages = parse_twee(open(SOURCE, encoding='utf-8').read())
    by_name = {p['name']: p for p in passages}
    title = by_name['StoryTitle']['text'].strip()
    data = json.loads(by_name['StoryData']['text'])
    css = by_name.get('StoryStylesheet', {'text': ''})['text']
    js = by_name.get('StoryScript', {'text': ''})['text']

    story = [p for p in passages if p['name'] not in ('StoryTitle', 'StoryData', 'StoryStylesheet', 'StoryScript')]
    pid = {p['name']: i + 1 for i, p in enumerate(story)}
    out = [f'<tw-storydata name="{esc(title)}" startnode="{pid[data["start"]]}" creator="Twine" creator-version="2.12.1" '
           f'format="{data["format"]}" format-version="{data["format-version"]}" ifid="{data["ifid"]}" '
           f'options="" tags="" zoom="1" hidden>',
           f'<style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css">{css}</style>',
           f'<script role="script" id="twine-user-script" type="text/twine-javascript">{js}</script>']
    for i, p in enumerate(story):
        pos = p['meta'].get('position', f'{100 + (i % 6) * 150},{100 + (i // 6) * 150}')
        size = p['meta'].get('size', '100,100')
        out.append(f'<tw-passagedata pid="{pid[p["name"]]}" name="{esc(p["name"])}" tags="{esc(" ".join(p["tags"]))}" '
                   f'position="{pos}" size="{size}">{esc(p["text"])}</tw-passagedata>')
    out.append('</tw-storydata>')

    template = open(TEMPLATE, encoding='utf-8').read()
    return (template.replace('{{TITLE}}', esc(title))
                    .replace('{{DESCRIPTION}}', esc(DESCRIPTION))
                    .replace('{{STORYDATA}}', ''.join(out)))


if __name__ == '__main__':
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(build())
    print('wrote', OUTPUT)
