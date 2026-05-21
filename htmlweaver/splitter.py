from bs4 import BeautifulSoup
from .utils import read_file, write_file, get_base_name, get_output_dir
import os


def split_html(html_file: str, output_dir: str = None) -> dict:
    """
    Split an HTML file into separate HTML, CSS, and JS files.
    Returns a dict with paths of created files.
    """
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return {}

    content = read_file(html_file)
    soup = BeautifulSoup(content, 'html.parser')

    base_name = get_base_name(html_file)
    out_dir = output_dir or get_output_dir(html_file)
    os.makedirs(out_dir, exist_ok=True)

    created_files = {}

    # ── استخراج CSS ──────────────────────────────────────────
    style_tags = soup.find_all('style')
    if style_tags:
        css_content = '\n\n'.join(tag.get_text() for tag in style_tags)
        css_path = os.path.join(out_dir, f"{base_name}.css")
        write_file(css_path, css_content.strip())
        created_files['css'] = css_path

        for tag in style_tags:
            tag.decompose()

        link_tag = soup.new_tag('link', rel='stylesheet', href=f"{base_name}.css")
        if soup.head:
            soup.head.append(link_tag)

    # ── استخراج JS ───────────────────────────────────────────
    script_tags = soup.find_all('script', src=False)
    if script_tags:
        js_content = '\n\n'.join(
            tag.get_text() for tag in script_tags if tag.get_text(strip=True)
        )
        if js_content.strip():
            js_path = os.path.join(out_dir, f"{base_name}.js")
            write_file(js_path, js_content.strip())
            created_files['js'] = js_path

            for tag in script_tags:
                if tag.get_text(strip=True):
                    tag.decompose()

            script_tag = soup.new_tag('script', src=f"{base_name}.js")
            if soup.body:
                soup.body.append(script_tag)

    # ── احفظ الـ HTML النظيف ──────────────────────────────────
    html_path = os.path.join(out_dir, f"{base_name}_split.html")
    write_file(html_path, soup.prettify())
    created_files['html'] = html_path

    print(f"\n🧵 htmlweaver split complete!")
    print(f"   Files created in: {out_dir}/")
    return created_files
