from __future__ import annotations

import html
import re
from pathlib import Path

import fitz


CORPUS_DIR = Path("data/demo_corpus")
OUTPUT_DIR = Path("data/raw_pdfs")
PAGE_MARKER = re.compile(r"^第\s+\d+\s+页\s*$", re.MULTILINE)


def split_pages(text: str) -> list[str]:
    parts = PAGE_MARKER.split(text)
    pages = [part.strip() for part in parts if part.strip()]
    if not pages:
        raise ValueError("语料中未找到有效页面内容")
    return pages


def text_to_html(text: str) -> str:
    escaped = html.escape(text).replace("\n", "<br/>")
    return (
        "<html><body style='font-family:sans-serif;font-size:11pt;line-height:1.45;'>"
        f"{escaped}"
        "</body></html>"
    )


def write_pdf_from_text(txt_path: Path, pdf_path: Path) -> None:
    pages = split_pages(txt_path.read_text(encoding="utf-8"))
    body = []
    for page_index, page_text in enumerate(pages, start=1):
        body.append(f"第 {page_index} 页")
        body.append(page_text)
    story = fitz.Story(text_to_html("\n".join(body)))

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    writer = fitz.DocumentWriter(str(pdf_path))
    mediabox = fitz.paper_rect("a4")

    while True:
        device = writer.begin_page(mediabox)
        more, _ = story.place(mediabox)
        story.draw(device)
        writer.end_page()
        if not more:
            break

    writer.close()


def main() -> None:
    corpus_files = sorted(CORPUS_DIR.glob("manual*.txt"))
    if not corpus_files:
        raise FileNotFoundError(
            f"找不到演示语料：{CORPUS_DIR}/manual*.txt。"
            "请确认已 clone 完整仓库。"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for txt_path in corpus_files:
        pdf_path = OUTPUT_DIR / f"{txt_path.stem}.pdf"
        write_pdf_from_text(txt_path, pdf_path)
        print(f"✅ 已生成: {pdf_path}")

    print(f"\n✅ 共生成 {len(corpus_files)} 份演示 PDF -> {OUTPUT_DIR}/")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(str(exc)) from exc
