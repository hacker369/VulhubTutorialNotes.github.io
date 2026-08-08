#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import hashlib
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
VULHUB = ROOT / "vulhub"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

pattern = re.compile(r"!\[([^\]]*)\]\[](https://cdn\.nlark\.com/[^)]+)\)")


def download(url: str) -> Path:
    ext = ".png"
    lower = url.lower()
    if ".jpg" in lower or ".jpeg" in lower:
        ext = ".jpg"
    elif ".gif" in lower:
        ext = ".gif"
    elif ".webp" in lower:
        ext = ".webp"

    name = hashlib.md5(url.encode()).hexdigest()[:16] + ext
    dest = IMG_DIR / name
    if dest.exists() and dest.stat().st_size > 0:
        return dest

    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urlopen(req, timeout=30).read()
    dest.write_bytes(data)
    print("downloaded:", dest.name, f"({len(data)} bytes)")
    time.sleep(0.3)
    return dest


def process_file(md: Path) -> bool:
    text = md.read_text(encoding="utf-8")
    state = {"changed": False}

    def repl(m):
        alt, url = m.group(1), m.group(2)
        local = download(url)
        rel = local.relative_to(ROOT).as_posix()
        state["changed"] = True
        return f"![{alt}]({rel})"

    new_text = pattern.sub(repl, text)
    if state["changed"]:
        md.write_text(new_text, encoding="utf-8")
        print("updated:", md.name)
        return True
    return False


def main():
    if not VULHUB.exists():
        print("找不到 vulhub 目录")
        return

    files = sorted(VULHUB.glob("*.md"))
    updated = 0
    for md in files:
        try:
            if process_file(md):
                updated += 1
        except Exception as e:
            print("失败:", md.name, "->", e)

    print("done")
    print(f"处理笔记: {len(files)} 篇, 更新: {updated} 篇")
    print(f"图片目录: {IMG_DIR}")


if __name__ == "__main__":
    main()
