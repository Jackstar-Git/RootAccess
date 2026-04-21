import re
from typing import List, Dict, Any, Final

class MarkdownConverter:
    def __init__(self, plugin_base_path: str = "/plugins/carousel"):
        self.plugin_path = plugin_base_path
        self.translation_table = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;"})
        
        self.inline_patterns = [
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

    def _reset_state(self):
        self.output: List[str] = []
        self.state = {
            "codeblock": False,
            "list": False,
            "blockquote": False,
            "html": False,
            "carousel": False
        }
        self.carousel_count = 0
        self.carousel_data: Dict[str, Any] = {}
        self.assets_injected = False

    @classmethod
    def quick_convert(cls, markdown_text: str) -> str:
        converter = cls()
        return converter.convert(markdown_text)

    def convert(self, markdown_text: str) -> str:
        self._reset_state()
        
        markdown_text = re.sub(
            r'{indent}(.*?){/indent}', 
            r'\n<div style="padding-left: 2em;">\n\1\n</div>\n', 
            markdown_text, flags=re.DOTALL
        )

        lines = markdown_text.splitlines()
        for line in lines:
            self._process_line(line)

        self._close_open_tags()
        return "\n".join(self.output)

    def _process_line(self, line: str):
        stripped = line.strip()

        if self._handle_state_toggles(stripped, line):
            return

        if self.state["html"]:
            self.output.append(line)
            return
        if self.state["codeblock"]:
            self.output.append(line.translate(self.translation_table))
            return
        if self.state["carousel"]:
            self._parse_carousel_line(stripped)
            return

        if not stripped:
            self._handle_empty_line()
            return

        self._parse_standard_line(stripped)

    def _handle_state_toggles(self, stripped: str, original_line: str) -> bool:
        if stripped.startswith("{html}"):
            self.state["html"] = True
            return True
        if stripped == "{/html}":
            self.state["html"] = False
            return True
        if stripped.startswith("```"):
            self.state["codeblock"] = not self.state["codeblock"]
            self.output.append("<pre>" if self.state["codeblock"] else "</pre>")
            return True
        if stripped.startswith("{carousel"):
            self._start_carousel(stripped)
            return True
        if stripped == "{/carousel}":
            self._end_carousel()
            return True
        return False

    def _start_carousel(self, line: str):
        self.state["carousel"] = True
        self.carousel_count += 1
        if not self.assets_injected:
            self.output.append(f'<link rel="stylesheet" href="{self.plugin_path}/carousel.css">')
            self.output.append(f'<script src="{self.plugin_path}/Carousel.js" defer></script>')
            self.assets_injected = True
        
        params = line.replace("{carousel", "").replace("}", "").replace(":", "").strip()
        self.carousel_data = {"auto": "true", "delay": "5000", "speed": "800", "indicators": "false", "items": []}
        for p in params.split():
            if "=" in p:
                k, v = p.split("=", 1)
                if k == "disable-indicators": self.carousel_data["indicators"] = v
                else: self.carousel_data[k] = v

    def _parse_carousel_line(self, stripped: str):
        img_match = re.search(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            self.carousel_data["items"].append({"alt": img_match.group(1), "src": img_match.group(2)})

    def _end_carousel(self):
        self.state["carousel"] = False
        d = self.carousel_data
        html = [
            f'<div class="carousel" data-auto="{d["auto"]}" data-delay="{d["delay"]}" '
            f'data-speed="{d["speed"]}" data-disable-indicators="{d["indicators"]}">',
            '  <div class="carousel-inner">'
        ]
        for i, item in enumerate(d["items"]):
            active = " active" if i == 0 else ""
            html.append(f'    <div class="carousel-item{active}"><img src="{item["src"]}" alt="{item["alt"]}"></div>')
        
        html.extend(['  </div>', '  <button class="prev-btn">Previous</button>', '  <button class="next-btn">Next</button>', '</div>'])
        self.output.append("\n".join(html))

    def _parse_media(self, text: str) -> str:
        def _get_style(attr_str):
            if not attr_str: return ""
            styles = []
            width = re.search(r'width=([^\s}]+)', attr_str)
            height = re.search(r'height=([^\s}]+)', attr_str)
            if height: styles.append(f"height:{height.group(1)};")
            if width: styles.append(f"width:{width.group(1)};")
            if "align=center" in attr_str: styles.append("display:block;margin-inline:auto;")
            elif "align=left" in attr_str: styles.append("float:left;")
            elif "align=right" in attr_str: styles.append("float:right;")
            return f' style="{" ".join(styles)}"' if styles else ""

        text = re.sub(r'!\[(.*?)\]\((.*?)\)(?:\{([^}]+)\})?', lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}"{_get_style(m.group(3))}>', text)
        text = re.sub(r'\[video\((.*?)\)\](?:\{([^}]+)\})?', lambda m: f'<video src="{m.group(1)}" controls{_get_style(m.group(2))}></video>', text)
        return text

    def _parse_standard_line(self, stripped: str):
        is_list = stripped.startswith("- ") and not stripped.startswith("\\- ")
        is_quote = stripped.startswith("> ") and not stripped.startswith("\\> ")
        is_header = stripped.startswith("#") and not stripped.startswith("\\#")
        
        clean_text = stripped
        h_level = 0

        if is_list or is_quote: clean_text = stripped[2:]
        elif is_header:
            m = re.match(r'#+', stripped)
            h_level = len(m.group(0))
            clean_text = stripped[h_level:].strip()

        clean_text = self._parse_media(clean_text)
        for pattern, replacement in self.inline_patterns:
            clean_text = pattern.sub(replacement, clean_text)
        
        for char in ['*', '_', '~', '{', '#', '-', '[', '^']:
            clean_text = clean_text.replace(f'\\{char}', char)

        self._manage_block_state("list", is_list, "<ul>", "</ul>")
        self._manage_block_state("blockquote", is_quote, "<blockquote>", "</blockquote>")

        if is_list: self.output.append(f"\t<li>{clean_text}</li>")
        elif is_quote: self.output.append(clean_text)
        elif is_header: self.output.append(f"<h{h_level}>{clean_text}</h{h_level}>")
        elif stripped.startswith("---"): self.output.append("<hr>")
        elif stripped.startswith("<div") or stripped.startswith("</div"): self.output.append(stripped)
        else: self.output.append(f"<p>{clean_text}</p>")

    def _manage_block_state(self, key, active_now, open_tag, close_tag):
        if active_now and not self.state[key]:
            self.state[key] = True
            self.output.append(open_tag)
        elif not active_now and self.state[key]:
            self.state[key] = False
            self.output.append(close_tag)

    def _handle_empty_line(self):
        for key, tag in [("list", "</ul>"), ("blockquote", "</blockquote>")]:
            if self.state[key]:
                self.output.append(tag)
                self.state[key] = False
        self.output.append("<span class='line-break'></span>")

    def _close_open_tags(self):
        if self.state["list"]: self.output.append("</ul>")
        if self.state["blockquote"]: self.output.append("</blockquote>")
        if self.state["codeblock"]: self.output.append("</pre>")