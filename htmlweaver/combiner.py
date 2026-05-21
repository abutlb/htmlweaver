import os
from bs4 import BeautifulSoup
from .utils import read_file, write_file, validate_file


def combine_html(
    html_file: str,
    css_file: str = None,
    js_file: str = None,
    output_file: str = None
) -> bool:
    """
    Combine separate HTML, CSS, and JS files into a single HTML file.
    Returns True on success, False on failure.
    """

    # ── التحقق من الملفات ─────────────────────────────────────
    if not validate_file(html_file, '.html'):
        return False
    if css_file and not validate_file(css_file, '.css'):
        return False
    if js_file and not validate_file(js_file, '.js'):
        return False

    html_content = read_file(html_file)
    soup = BeautifulSoup(html_content, 'html.parser')

    # ── دمج CSS ──────────────────────────────────────────────
    if css_file:
        css_content = read_file(css_file)

        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href') or ''
            if os.path.basename(css_file) in href:
                link.decompose()

        style_tag = soup.new_tag('style')
        style_tag.string = f"\n{css_content}\n"
        if soup.head:
            soup.head.append(style_tag)

    # ── دمج JS ───────────────────────────────────────────────
    if js_file:
        js_content = read_file(js_file)

        for script in soup.find_all('script', src=True):
            src = script.get('src') or ''
            if os.path.basename(js_file) in src:
                script.decompose()

        script_tag = soup.new_tag('script')
        script_tag.string = f"\n{js_content}\n"
        if soup.body:
            soup.body.append(script_tag)

    # ── احفظ الملف المدموج ───────────────────────────────────
    if not output_file:
        base = os.path.splitext(html_file)[0]
        output_file = f"{base}_combined.html"

    write_file(output_file, soup.prettify())
    print(f"\n🧵 htmlweaver weave complete!")
    print(f"   Output: {output_file}")
    return True
