from logging_utility import logger
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from typing import Tuple, List

def generate_captcha() -> Tuple[Image.Image, List[str]]:
    width: int = 350
    height: int = 80
    image: Image.Image = Image.new("RGB", (width, height), "white")
    font_path: str = "Helvetica.ttf"

    letters: str = "ABCDEFGHJKLMNPQRSTUVWYZ123456789abcdefghijkmnpqrstuvwyz"
    text: List[str] = random.choices(letters, k=random.randint(7, 10))

    draw: ImageDraw.Draw = ImageDraw.Draw(image)
    x: int = 10

    for char in text:
        font_size: int = random.randint(20, 55)
        angle: int = random.randint(-35, 35)

        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width, char_height = bbox[2] - bbox[0], bbox[3] - bbox[1] + 5
        char_image = Image.new("RGBA", (char_width * 2, char_height * 2), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((char_width // 2, char_height // 2), char, font=font, fill="black")

        char_image = char_image.rotate(angle, expand=True, resample=Image.BICUBIC)

        image.paste(char_image, (x, height // 2 - char_image.size[1] // 2), char_image)
        x += char_width + random.randint(7, 8)

    for _ in range(random.randint(750, 1000)):
        x_noise: int = random.randint(0, width - 1)
        y_noise: int = random.randint(0, height - 1)
        draw.point((x_noise, y_noise), fill=(0,0,0))

    for _ in range(random.randint(4, 7)):
        x_start: int = random.randint(0, width)
        y_start: int = random.randint(0, height)
        x_end: int = random.randint(0, width)
        y_end: int = random.randint(0, height)
        draw.line((x_start, y_start, x_end, y_end), fill=(40,40,40), width=random.randint(1,3))

    image = image.filter(ImageFilter.GaussianBlur(0.25))
    return (image, "".join(text))

def convert_markdown_to_html(markdown_text: str) -> str:
    translation_table: dict = str.maketrans({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    })
    
    patterns: List[Tuple[re.Pattern, str]] = [
        (re.compile(r'\*\*\*(.+?)\*\*\*'), r'<strong><em>\1</em></strong>'),
        (re.compile(r'\*\*(.+?)\*\*'), r'<strong>\1</strong>'),          
        (re.compile(r'\*(.+?)\*'), r'<em>\1</em>'),                        
        (re.compile(r'~~(.+?)~~'), r'<s>\1</s>'),                         
        (re.compile(r'_(.+?)_'), r'<u>\1</u>'),                               
        (re.compile(r'\{color:(#[0-9a-fA-F]{3,6})\}(.*?)\{\/color\}', re.DOTALL), r'<div style="color:\1">\2</div>'),
        (re.compile(r'\{align:([a-z]*)\}(.*?)\{\/align\}', re.DOTALL), r'<div style="display: block; text-align:\1">\2</div>'),
        (re.compile(r'\[(.+?)\]\((.+?)\)'), r'<a href="\2">\1</a>'),        
        (re.compile(r'`(.+?)`'), r'<code>\1</code>')
    ]

    html_output_list: List[str] = []

    line_iter = iter(markdown_text.splitlines())

    in_codeblock: bool = False
    in_list: bool = False
    in_blockquote: bool = False
    in_html: bool = False

    for line in line_iter:
        if line.strip().startswith(r"{html}"):
            in_html = True
            continue
        if line.strip().startswith(r"{/html}"):
            in_html = False
            continue
        
        if in_html:
            html_output_list.append(line)
            continue

        if line.strip().startswith('```'):
            if in_codeblock:
                html_output_list.append('</pre>')
                in_codeblock = False
            else:
                html_output_list.append('<pre>')
                in_codeblock = True
            continue

        if in_codeblock:
            line = line.translate(translation_table)
            html_output_list.append(line)
            continue

        if in_list and not line.strip().startswith('- '):
            html_output_list.append('</ul>')
            in_list = False
        
        if in_blockquote and not line.strip().startswith('> '):
            html_output_list.append('</blockquote>')
            in_blockquote = False

        for pattern, replacement in patterns:
            line = pattern.sub(replacement, line)

        if line.strip() == "":
            html_output_list.append("<br>")
            continue

        if line.strip().startswith('#'):
            header_level: int = len(re.match(r'#+', line).group(0))
            header_content: str = line[header_level:].strip()
            html_output_list.append(f'<h{header_level}>{header_content}</h{header_level}>')
            continue

        if line.strip().startswith("---"):
            html_output_list.append("<hr>")
            continue

        if line.strip().startswith('- '):
            if not in_list:
                in_list = True
                html_output_list.append('<ul>')
            html_output_list.append(f'\t<li>{line[2:].strip()}</li>')
            continue

        if line.strip().startswith('> '):
            if not in_blockquote:
                in_blockquote = True
                html_output_list.append('<blockquote>')
            html_output_list.append(line[2:].strip())
            continue

        html_output_list.append(f'<p>{line.strip()}</p>')

    if in_list:
        html_output_list.append('</ul>')
    if in_blockquote:
        html_output_list.append('</blockquote>')
    if in_codeblock:
        html_output_list.append('</pre>')

    html_output: str = "\n".join(html_output_list)

    return html_output

def format_number(number: float|int, format_string: str) -> str:
    number = float(number)
    pattern: str = r'^(?P<Pre_text>.*?)(?P<thousands_digits>[#0]+)(?P<thousands_separator>[^#0]*?)(?P<hundreds_digits>[#0]{1,3})(?P<decimal>[\s\S]*?)(?P<num_of_decimals>[#0]+)(?P<post_text>[\s\S]*)$'
    match: re.Match = re.match(pattern, format_string)

    if not match:
        return f"{number:,.2f}"

    pre_text: str = match.group("Pre_text") or ""
    thousands_digits: str = match.group("thousands_digits") or ""
    hundreds_digits: str = match.group("hundreds_digits") or ""
    thousands_separator: str = match.group("thousands_separator") or ""
    decimal: str = match.group("decimal")
    num_of_decimals: str = match.group("num_of_decimals") or "00"
    post_text: str = match.group("post_text") or ""

    decimal_places: int = len(num_of_decimals)

    pre_digits: int = str(thousands_digits+hundreds_digits)[::-1].rfind("0") + 1

    min_digits: int = str(num_of_decimals).rfind("0") + 1
    if pre_digits < 1:
        pre_digits = 0
    
    if min_digits < 1:
        min_digits = 0

    if not decimal:
        formatted_number: str = f"{int(number)}" if number.is_integer() else f"{number:,.2f}"
    else:
        formatted_number: str = f"{number:,.{decimal_places}f}"

    decimal_original: str = str(number).split(".")[1] if not number.is_integer() else ""
    integer_part: str = str(number).split(".")[0].rjust(pre_digits, "0")

    if not thousands_separator:
        formatted_integer_part: str = integer_part
    else:
        int_str: str = ""
        for i, char in enumerate(integer_part[::-1]):
            if i % 3 == 0 and i != 0:
                int_str += thousands_separator
            int_str += char
        formatted_integer_part = int_str[::-1]

    if decimal_original or min_digits > 0:
        formatted_number = f"{formatted_integer_part}{decimal}{decimal_original[:decimal_places].ljust(min_digits, '0')}"
    else:
        formatted_number = formatted_integer_part

    if number == 0:
        formatted_number = f"{formatted_integer_part}{decimal}{'0' * min_digits}"

    formatted_string: str = f"{pre_text}{formatted_number}{post_text}"

    return formatted_string
