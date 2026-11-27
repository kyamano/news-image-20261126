# The World in One Day — Thursday 26 November 2026

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261126/kyamano/news-image-20261126/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261126/kyamano/news-image-20261126/reward.svg)](https://make.fun)

Entry for the make.fun competition **news-image-20261126**:
"Sum up 2026-11-26's world news in one image."

## What it is

A newspaper-style front page summing up Thursday 26 November 2026 in one
1024×1024 image: 10 detailed stories, 20 briefs, and a "day in numbers" box.

Headlines include the Iranian drone strike that killed two Italians in Kuwait,
two tankers hitting mines in the Strait of Hormuz, Kim Jong Un's nuclear-site
tour, Myanmar's rejection of parts of the ICJ ruling, UK net migration falling
to 77,000, Trump's Thanksgiving message, the Bangkok refinery blast,
Guinea-Bissau delaying its election to 2028, the EU's EUR 45bn Ukraine loan,
and Pablo Hernandez de Cos being picked to lead the ECB.

Every story was checked against two or more outlets, and only events that
happened — or were first reported — on 26 November 2026 are included.
Research notes: `../news-image-20261126-notes.md` (kept outside this repo).

## How it works

`main.py` (Python 3.13, standard library only, no network) draws the page
with a built-in 5×7 bitmap font and a small pure-Python PNG encoder, and
writes `entry.png` (1024×1024, under 1 MiB). It is fully deterministic:
running it twice produces byte-identical output.

```sh
python3 main.py   # writes entry.png
```

## License

MIT — see [LICENSE](LICENSE).
