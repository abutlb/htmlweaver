import os
import re
from bs4 import BeautifulSoup
from ..utils import read_file, write_file, get_base_name, get_output_dir


def export_react(html_file: str, output_dir: str = None) -> str:
    """
    Convert an HTML file into a React functional component (.jsx).
    Returns the path of the created .jsx file.
    """
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return ""

    content = read_file(html_file)
    soup = BeautifulSoup(content, 'html.parser')

    base_name = get_base_name(html_file)
    component_name = _to_pascal_case(base_name)
    out_dir = output_dir or get_output_dir(html_file)
    os.makedirs(out_dir, exist_ok=True)

    # ── استخراج CSS ──────────────────────────────────────────
    style_tags = soup.find_all('style')
    css_content = '\n'.join(tag.get_text() for tag in style_tags).strip()
    for tag in style_tags:
        tag.decompose()

    # احفظ CSS في ملف منفصل (React convention)
    css_path = ""
    if css_content:
        css_path = os.path.join(out_dir, f"{component_name}.css")
        write_file(css_path, css_content)

    # ── استخراج JS ───────────────────────────────────────────
    script_tags = soup.find_all('script', src=False)
    js_content = '\n'.join(
        tag.get_text() for tag in script_tags if tag.get_text(strip=True)
    ).strip()
    for tag in script_tags:
        if tag.get_text(strip=True):
            tag.decompose()

    # ── استخراج HTML ─────────────────────────────────────────
    body = soup.body
    if body:
        template_content = ''.join(str(child) for child in body.children).strip()
    else:
        template_content = str(soup).strip()

    # ── تحويل HTML attributes إلى JSX ────────────────────────
    template_content = _html_to_jsx(template_content)

    # ── تحليل JS ─────────────────────────────────────────────
    state_vars = _extract_variables(js_content)
    functions = _extract_functions(js_content)

    # ── بناء الـ React Component ──────────────────────────────
    jsx_output = _build_react_component(
        component_name=component_name,
        template=template_content,
        state_vars=state_vars,
        functions=functions,
        css_import=f"{component_name}.css" if css_path else None
    )

    jsx_path = os.path.join(out_dir, f"{component_name}.jsx")
    write_file(jsx_path, jsx_output)

    print(f"\n⚛️  React component created: {jsx_path}")
    return jsx_path


def _to_pascal_case(name: str) -> str:
    return ''.join(word.capitalize() for word in re.split(r'[-_]', name))


def _html_to_jsx(html: str) -> str:
    """Convert HTML attributes to JSX-compatible syntax."""
    # class → className
    html = re.sub(r'\bclass="', 'className="', html)
    # for → htmlFor
    html = re.sub(r'\bfor="', 'htmlFor="', html)
    # onclick → onClick
    html = re.sub(r'\bonclick="', 'onClick={() => ', html)
    html = re.sub(r'\boninput="', 'onInput={() => ', html)
    html = re.sub(r'\bonchange="', 'onChange={() => ', html)
    html = re.sub(r'\bonsubmit="', 'onSubmit={(e) => { e.preventDefault(); ', html)
    html = re.sub(r'\bonkeydown="', 'onKeyDown={() => ', html)
    html = re.sub(r'\bonkeyup="', 'onKeyUp={() => ', html)
    # Self-closing tags
    for tag in ['input', 'img', 'br', 'hr', 'meta', 'link']:
        html = re.sub(
            rf'<({tag})([^>]*?)(?<!/)>',
            rf'<\1\2 />',
            html,
            flags=re.IGNORECASE
        )
    # style="..." → style={{ ... }} (inline styles)
    def convert_inline_style(match):
        styles = match.group(1)
        # حوّل CSS properties إلى camelCase
        props = []
        for prop in styles.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, val = prop.split(':', 1)
                key = _css_to_camel(key.strip())
                val = val.strip()
                props.append(f'{key}: "{val}"')
        return 'style={{{{ {} }}}}'.format(', '.join(props))

    html = re.sub(r'style="([^"]*)"', convert_inline_style, html)
    return html


def _css_to_camel(prop: str) -> str:
    """Convert CSS property to camelCase: background-color → backgroundColor"""
    parts = prop.split('-')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def _extract_variables(js: str) -> dict:
    vars_found = {}
    pattern = re.compile(
        r'\b(?:let|var|const)\s+(\w+)\s*=\s*([^;]+);', re.MULTILINE
    )
    for match in pattern.finditer(js):
        vars_found[match.group(1)] = match.group(2).strip()
    return vars_found


def _extract_functions(js: str) -> list:
    functions = []
    pattern = re.compile(
        r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE
    )
    for match in pattern.finditer(js):
        func_name = match.group(1)
        func_params = match.group(2).strip()
        start = match.end()
        depth = 1
        i = start
        while i < len(js) and depth > 0:
            if js[i] == '{':
                depth += 1
            elif js[i] == '}':
                depth -= 1
            i += 1
        func_body = js[start:i - 1].strip()
        functions.append({
            'name': func_name,
            'params': func_params,
            'body': func_body
        })
    return functions


def _build_react_component(
    component_name: str,
    template: str,
    state_vars: dict,
    functions: list,
    css_import: str = None
) -> str:

    lines = ["import React, { useState } from 'react';"]

    if css_import:
        lines.append(f"import './{css_import}';")

    lines.append("")
    lines.append(f"export default function {component_name}() {{")

    # ── useState hooks ────────────────────────────────────────
    if state_vars:
        lines.append("  // State")
        for var, val in state_vars.items():
            setter = 'set' + var[0].upper() + var[1:]
            lines.append(f"  const [{var}, {setter}] = useState({val});")
        lines.append("")

    # ── functions ─────────────────────────────────────────────
    if functions:
        lines.append("  // Handlers")
        for fn in functions:
            params = fn['params']
            body = _indent(fn['body'], 4)
            lines.append(f"  function {fn['name']}({params}) {{")
            lines.append(body)
            lines.append("  }")
            lines.append("")

    # ── return JSX ────────────────────────────────────────────
    lines.append("  return (")
    lines.append("    <div>")
    for line in template.splitlines():
        lines.append(f"      {line}")
    lines.append("    </div>")
    lines.append("  );")
    lines.append("}")
    lines.append("")

    return '\n'.join(lines)


def _indent(text: str, spaces: int) -> str:
    pad = ' ' * spaces
    return '\n'.join(pad + line if line.strip() else line for line in text.splitlines())
