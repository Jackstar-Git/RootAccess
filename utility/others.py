import re
from typing import List, Tuple, Pattern, Final

def convert_markdown_to_html(markdown_text: str) -> str:
    translation_table: Final[dict[int, str]] = str.maketrans({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    })

    patterns: Final[List[Tuple[Pattern[str], str]]] = [
        (re.compile(r'(?<!\\)\*\*\*(.+?)\*\*\*'), r'<strong><em>\1</em></strong>'),
        (re.compile(r'(?<!\\)\*\*(.+?)\*\*'), r'<strong>\1</strong>'),
        (re.compile(r'(?<!\\)\*(.+?)\*'), r'<em>\1</em>'),
        (re.compile(r'(?<!\\)~~(.+?)~~'), r'<s>\1</s>'),
        (re.compile(r'(?<!\\)_(.+?)_'), r'<u>\1</u>'),
        (re.compile(r'(?<!\\)\[\^(.+?)\]'), r'<sup>\1</sup>'),
        (re.compile(r'(?<!\\)\[_(.+?)\]'), r'<sub>\1</sub>'),
        (re.compile(r'(?<!\\)\{color:(#[0-9a-fA-F]{3,6})\}(.*?)\{\/color\}', re.DOTALL), r'<span style="color:\1">\2</span>'),
        (re.compile(r'(?<!\\)\{align:([a-z]*)\}(.*?)\{\/align\}', re.DOTALL), r'<span style="display: inline-block; width: 100%; text-align:\1">\2</span>'),
        (re.compile(r'(?<!\\)\[(.+?)\]\((.+?)\)'), r'<a href="\2">\1</a>'),
        (re.compile(r'(?<!\\)`(.+?)`'), r'<code>\1</code>')
    ]

    html_output: List[str] = []
    lines: List[str] = markdown_text.splitlines()

    state: dict[str, bool] = {
        "codeblock": False,
        "list": False,
        "blockquote": False,
        "html": False
    }

    for line in lines:
        stripped: str = line.strip()

        if stripped.startswith("{html}"):
            state["html"] = True
            continue
        if stripped.startswith("{/html}"):
            state["html"] = False
            continue
        if state["html"]:
            html_output.append(line)
            continue

        if stripped.startswith("```"):
            state["codeblock"] = not state["codeblock"]
            html_output.append("</pre>" if not state["codeblock"] else "<pre>")
            continue

        if state["codeblock"]:
            html_output.append(line.translate(translation_table))
            continue

        is_list: bool = stripped.startswith("- ") and not stripped.startswith("\\- ")
        is_quote: bool = stripped.startswith("> ") and not stripped.startswith("\\> ")
        is_header: bool = stripped.startswith("#") and not stripped.startswith("\\#")
        is_hr: bool = stripped.startswith("---") and not stripped.startswith("\\---")

        clean_text: str = stripped
        header_level: int = 0

        if is_list or is_quote:
            clean_text = stripped[2:]
        elif is_header:
            match = re.match(r'#+', stripped)
            header_level = len(match.group(0)) if match else 0
            clean_text = stripped[header_level:].strip()

        for pattern, replacement in patterns:
            clean_text = pattern.sub(replacement, clean_text)

        for char in ['*', '_', '~', '{', '#', '-', '[', '^']:
            clean_text = clean_text.replace(f'\\{char}', char)

        if is_list:
            if not state["list"]:
                state["list"] = True
                html_output.append("<ul>")
            html_output.append(f"\t<li>{clean_text}</li>")
            continue
        elif state["list"]:
            html_output.append("</ul>")
            state["list"] = False

        if is_quote:
            if not state["blockquote"]:
                state["blockquote"] = True
                html_output.append("<blockquote>")
            html_output.append(clean_text)
            continue
        elif state["blockquote"]:
            html_output.append("</blockquote>")
            state["blockquote"] = False

        if not clean_text and not stripped:
            html_output.append("<br>")
            continue

        if is_header:
            html_output.append(f"<h{header_level}>{clean_text}</h{header_level}>")
        elif is_hr:
            html_output.append("<hr>")
        else:
            html_output.append(f"<p>{clean_text}</p>")

    if state["list"]: html_output.append("</ul>")
    if state["blockquote"]: html_output.append("</blockquote>")
    if state["codeblock"]: html_output.append("</pre>")

    return "\n".join(html_output)