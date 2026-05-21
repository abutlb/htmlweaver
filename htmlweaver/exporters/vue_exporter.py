import os
import re
from bs4 import BeautifulSoup
from ..utils import read_file, write_file, get_base_name, get_output_dir


def export_vue(html_file: str, output_dir: str = None) -> str:
    """
    Convert an HTML file into a Vue Single File Component (.vue).
    Returns the path of the created .vue file.
    """
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return ""

    content = read_file(html_file)
    soup = BeautifulSoup(content, 'html.parser')

    base_name = get_base_name(html_file)
    # حوّل اسم الملف إلى PascalCase مثل my-page → MyPage
    component_name = _to_pascal_case(base_name)
    out_dir = output_dir or get_output_dir(html_file)
    os.makedirs(out_dir, exist_ok=True)

    # ── استخراج CSS ──────────────────────────────────────────
    style_tags = soup.find_all('style')
    css_content = '\n'.join(tag.get_text() for tag in style_tags).strip()
    for tag in style_tags:
        tag.decompose()

    # ── استخراج JS ───────────────────────────────────────────
    script_tags = soup.find_all('script', src=False)
    js_content = '\n'.join(
        tag.get_text() for tag in script_tags if tag.get_text(strip=True)
    ).strip()
    for tag in script_tags:
        if tag.get_text(strip=True):
            tag.decompose()

    # ── استخراج HTML (محتوى الـ body فقط) ───────────────────
    body = soup.body
    if body:
        # خذ محتوى الـ body بدون الوسم نفسه
        template_content = ''.join(str(child) for child in body.children).strip()
    else:
        template_content = str(soup).strip()

    # ── تحويل Event Handlers ─────────────────────────────────
    # onclick="fn()" → @click="fn()"
    template_content = re.sub(r'\bonclick="', '@click="', template_content)
    template_content = re.sub(r'\boninput="', '@input="', template_content)
    template_content = re.sub(r'\bonchange="', '@change="', template_content)
    template_content = re.sub(r'\bonsubmit="', '@submit.prevent="', template_content)
    template_content = re.sub(r'\bonkeydown="', '@keydown="', template_content)
    template_content = re.sub(r'\bonkeyup="', '@keyup="', template_content)
    template_content = re.sub(r'\bonmouseover="', '@mouseover="', template_content)
    template_content = re.sub(r'\bonmouseout="', '@mouseout="', template_content)

    # ── تحليل JS واستخراج data و methods ─────────────────────
    data_vars = _extract_variables(js_content)
    methods = _extract_functions(js_content)

    # ── بناء الـ Vue Component ────────────────────────────────
    vue_output = _build_vue_component(
        component_name=component_name,
        template=template_content,
        data_vars=data_vars,
        methods=methods,
        css=css_content
    )

    vue_path = os.path.join(out_dir, f"{component_name}.vue")
    write_file(vue_path, vue_output)

    print(f"\n⚡ Vue component created: {vue_path}")
    return vue_path


def _to_pascal_case(name: str) -> str:
    """Convert kebab-case or snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in re.split(r'[-_]', name))


def _extract_variables(js: str) -> dict:
    """Extract top-level let/var/const declarations."""
    vars_found = {}
    pattern = re.compile(
        r'\b(?:let|var|const)\s+(\w+)\s*=\s*([^;]+);', re.MULTILINE
    )
    for match in pattern.finditer(js):
        name = match.group(1)
        value = match.group(2).strip()
        vars_found[name] = value
    return vars_found


def _extract_functions(js: str) -> list:
    """Extract top-level function declarations."""
    functions = []
    pattern = re.compile(
        r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE
    )
    # نجيب كل الـ functions مع محتواها
    for match in pattern.finditer(js):
        func_name = match.group(1)
        func_params = match.group(2).strip()
        start = match.end()
        # نحسب الـ braces علشان نجيب المحتوى الكامل
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


def _build_vue_component(
    component_name: str,
    template: str,
    data_vars: dict,
    methods: list,
    css: str
) -> str:
    """Assemble the final .vue file content."""

    # ── <template> ───────────────────────────────────────────
    template_block = f"<template>\n  <div>\n{_indent(template, 4)}\n  </div>\n</template>"

    # ── data() ───────────────────────────────────────────────
    if data_vars:
        data_lines = ',\n'.join(
            f"      {k}: {v}" for k, v in data_vars.items()
        )
        data_block = f"    data() {{\n      return {{\n{data_lines}\n      }};\n    }},"
    else:
        data_block = "    data() {\n      return {};\n    },"

    # ── methods ───────────────────────────────────────────────
    if methods:
        method_lines = []
        for fn in methods:
            params = fn['params']
            body = _indent(fn['body'], 6)
            method_lines.append(f"    {fn['name']}({params}) {{\n{body}\n    }}")
        methods_block = "    methods: {\n" + ",\n".join(method_lines) + "\n    },"
    else:
        methods_block = "    methods: {},"

    # ── <script> ─────────────────────────────────────────────
    script_block = (
        f"<script>\nexport default {{\n"
        f"  name: '{component_name}',\n"
        f"  {data_block}\n"
        f"  {methods_block}\n"
        f"}};\n</script>"
    )

    # ── <style scoped> ────────────────────────────────────────
    if css:
        style_block = f"<style scoped>\n{css}\n</style>"
    else:
        style_block = "<style scoped>\n</style>"

    return f"{template_block}\n\n{script_block}\n\n{style_block}\n"


def _indent(text: str, spaces: int) -> str:
    """Indent every line of text by N spaces."""
    pad = ' ' * spaces
    return '\n'.join(pad + line if line.strip() else line for line in text.splitlines())
