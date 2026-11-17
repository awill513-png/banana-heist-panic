"""Checks for the Twine (Harlowe) version. Run: python3 -I -m unittest discover -s tests -v  (from repo root)"""
import html
import importlib.util
import os
import re
import unittest
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECIAL = {'StoryTitle', 'StoryData', 'StoryStylesheet', 'StoryScript'}


def load_build():
    spec = importlib.util.spec_from_file_location('build', os.path.join(ROOT, 'tools', 'build.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def targets(text):
    out = []
    for raw in re.findall(r'\[\[(.+?)\]\]', text):
        if '->' in raw:
            out.append(raw.split('->')[-1])
        elif '<-' in raw:
            out.append(raw.split('<-')[0])
        else:
            out.append(raw)
    out += [m[1] for m in re.findall(r'\(go-to:\s*(["\'])(.+?)\1\)', text)]
    return [t.strip() for t in out]


class TwineStory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = load_build()
        cls.passages = cls.build.parse_twee(open(os.path.join(ROOT, 'source.twee'), encoding='utf-8').read())
        cls.story = {p['name']: p for p in cls.passages if p['name'] not in SPECIAL and 'header' not in p['tags']}

    def test_links_resolve(self):
        for name, p in self.story.items():
            for t in targets(p['text']):
                self.assertIn(t, self.story, f'{name} -> {t}')

    def test_no_dead_ends(self):
        for name, p in self.story.items():
            if 'ending' in p['tags']:
                continue
            choices = len(re.findall(r'\[\[.+?\]\]', p['text'])) + len(re.findall(r'\(link:', p['text']))
            if name == 'Finale':
                choices = len(targets(p['text']))
            self.assertGreaterEqual(choices, 2, f'{name} dead end')

    def test_all_reachable(self):
        seen, q = {'Start'}, deque(['Start'])
        while q:
            for t in targets(self.story[q.popleft()]['text']):
                if t not in seen:
                    seen.add(t)
                    q.append(t)
        self.assertEqual(sorted(set(self.story) - seen), [])

    def test_three_endings_and_size(self):
        self.assertEqual(sum('ending' in p['tags'] for p in self.story.values()), 3)
        self.assertTrue(30 <= len(self.story) <= 36, len(self.story))

    def test_characters_present(self):
        text = ' '.join(p['text'] for p in self.story.values()).lower()
        for w in ['gru', 'lucy', 'margo', 'edith', 'agnes', 'kyle', 'minion', 'unicorn', 'fart gun', 'snoozemonger']:
            self.assertIn(w, text)

    def test_images_exist_and_have_alt(self):
        refs = 0
        for name, p in self.story.items():
            for tag in re.findall(r'<img [^>]*>', p['text']):
                refs += 1
                src = re.search(r'src="([^"]+)"', tag).group(1)
                self.assertTrue(os.path.isfile(os.path.join(ROOT, src)), f'{name}: {src}')
                self.assertRegex(tag, r'alt="[^"]+"', f'{name}: no alt')
        self.assertGreater(refs, 30)

    def test_every_scene_has_a_picture(self):
        for name, p in self.story.items():
            if name in ('Finale',):
                continue
            self.assertIn('<img ', p['text'], f'{name} has no picture')

    def test_stats_reset_on_new_game(self):
        start = self.story['Start']['text']
        self.assertRegex(start, r'\(set: \$bananas to 0, \$chaos to 0\)')

    def test_endings_tracker_safe_without_title_screen(self):
        for name, p in self.story.items():
            if 'ending' in p['tags']:
                guard = p['text'].find('(unless: $endings is a dataset)[(set: $endings to (ds:))]')
                add = p['text'].find('(set: $endings to it + (ds:')
                self.assertTrue(0 <= guard < add, f'{name} adds to $endings before making sure it exists')

    def test_built_html_matches_source(self):
        built = self.build.build()
        on_disk = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
        self.assertEqual(built, on_disk, 'index.html is stale: run python3 -I tools/build.py')
        self.assertIn('format="Harlowe" format-version="3.3.9"', on_disk)
        pdata = re.findall(r'<tw-passagedata pid="(\d+)" name="([^"]*)"[^>]*>(.*?)</tw-passagedata>', on_disk, re.S)
        names = {html.unescape(n): pid for pid, n, _ in pdata}
        self.assertEqual(len(pdata), len(self.passages) - len(SPECIAL & {p['name'] for p in self.passages}))
        start_pid = re.search(r'<tw-storydata[^>]*startnode="(\d+)"', on_disk).group(1)
        self.assertEqual(names['Start'], start_pid)
        for pid, n, body in pdata:
            src = next(p for p in self.passages if p['name'] == html.unescape(n))
            self.assertEqual(html.unescape(body), src['text'])


if __name__ == '__main__':
    unittest.main()
