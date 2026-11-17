# Banana Heist Panic

A funny choose-your-own-adventure Twine game (Harlowe 3.3.9). Dr. Snoozemonger has stolen every banana on Earth to power his Eternal Nap Ray, and it's up to Gru, Lucy, Margo, Edith, Agnes, Kyle, the Minions, the fluffy unicorn, and the fart gun to stop him.

**Play it:** https://awill513-png.github.io/banana-heist-panic/

## Files

| File | What it is |
|------|------------|
| `index.html` | The playable Twine game (this is what GitHub Pages shows) |
| `source.twee` | Twee source of the story. In Twine, use **Library → Import** to keep editing |
| `img/` | Original pictures: character cards and props (SVG) |
| `tools/build.py` | Rebuilds `index.html` from `source.twee` |
| `tools/harlowe-3.3.9-template.html` | The Harlowe story format engine that `build.py` fills in |
| `tests/test_twine.py` | Story checks: links, dead ends, reachability, pictures, endings |
| `docs/` | Design and plan |

## The game
- 4 chapters, 30 story scenes, 3 silly "oops" scenes you can rewind from, and **3 endings**: Hero, Total Chaos, and Sleepy Victory.
- Two counters, **Bananas recovered** and **Minion chaos**, decide which ending you get.
- An "Endings discovered: X of 3" tracker encourages replaying.
- Every scene shows who is in it. Every picture has alt text.
- The layout works on phone screens.

## Editing
**In Twine:** Library → Import → `source.twee` (or `index.html`). The images load once the game is published next to the `img/` folder.

**By hand:** edit `source.twee`, then run:

```sh
python3 -I tools/build.py
python3 -I -m unittest discover -s tests -v
```

## Credits
- A non-commercial fan game made for fun. Gru, Lucy, Margo, Edith, Agnes, Kyle, and the Minions belong to Illumination and Universal Pictures.
- Dr. Snoozemonger, the story, and all pictures are original.
- Built with [Twine](https://twinery.org) and the Harlowe story format.
