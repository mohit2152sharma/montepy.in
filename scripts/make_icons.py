"""Generate the site icons in static/ from one shape definition.

The icons are a plain "M" monogram. Replace them with a real logo when one
exists: keep the same file names, because config.yml and the theme use them.

Usage: python3 scripts/make_icons.py   (needs Pillow)
"""
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"
BG = "#2e2e33"  # same value as the theme's default theme-color
FG = "#ffffff"
# "M" outline on a 100 x 100 grid.
M = [(20, 78), (20, 22), (33, 22), (50, 49), (67, 22), (80, 22), (80, 78),
     (67, 78), (67, 44), (50, 70), (33, 44), (33, 78)]


def mask_svg() -> str:
    """Single-colour shape for Safari pinned tabs."""
    pts = " ".join(f"{x},{y}" for x, y in M)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<polygon points="{pts}"/></svg>\n')


def png(size: int):
    from PIL import Image, ImageDraw  # only needed to draw, not to read M

    scale = 8  # draw large, then downsample for smooth edges
    big = size * scale
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 0.18, fill=BG)
    d.polygon([(x * big / 100, y * big / 100) for x, y in M], fill=FG)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    STATIC.mkdir(exist_ok=True)
    (STATIC / "safari-pinned-tab.svg").write_text(mask_svg())
    png(16).save(STATIC / "favicon-16x16.png", optimize=True)
    png(32).save(STATIC / "favicon-32x32.png", optimize=True)
    png(180).save(STATIC / "apple-touch-icon.png", optimize=True)
    png(512).save(STATIC / "logo-512.png", optimize=True)  # JSON-LD logo
    png(48).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


if __name__ == "__main__":
    main()
