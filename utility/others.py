import re

def convert_markdown_to_html(markdown_text: str) -> str:
    translation_table = str.maketrans({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    })
    
    patterns = [
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
    
    html_output_list = []
    line_iter = iter(markdown_text.splitlines())

    in_codeblock = False
    in_list = False
    in_blockquote = False
    in_html = False

    for line in line_iter:
        if line.strip().startswith("{html}"):
            in_html = True
            continue
        if line.strip().startswith("{/html}"):
            in_html = False
            continue
        if in_html:
            html_output_list.append(line)
            continue

        if line.strip().startswith("```"):
            if in_codeblock:
                html_output_list.append("</pre>")
                in_codeblock = False
            else:
                html_output_list.append("<pre>")
                in_codeblock = True
            continue

        if in_codeblock:
            html_output_list.append(line.translate(translation_table))
            continue

        processed_content = line.strip()
        
        # Check for escaped triggers
        is_list_item = processed_content.startswith('- ') and not processed_content.startswith('\\- ')
        is_quote_item = processed_content.startswith('> ') and not processed_content.startswith('\\> ')
        is_header = processed_content.startswith('#') and not processed_content.startswith('\\#')
        is_hr = processed_content.startswith('---') and not processed_content.startswith('\\---')

        clean_text = processed_content
        if is_list_item: clean_text = processed_content[2:]
        elif is_quote_item: clean_text = processed_content[2:]
        elif is_header:
            header_match = re.match(r'#+', processed_content)
            header_level = len(header_match.group(0))
            clean_text = processed_content[header_level:].strip()

        for pattern, replacement in patterns:
            clean_text = pattern.sub(replacement, clean_text)
        
        # Remove escape characters
        escape_chars = ['\\*', '\\_', '\\~', '\\{', '\\#', '\\-', '\\[', '\\^']
        for char in escape_chars:
            clean_text = clean_text.replace(char, char[-1])

        if is_list_item:
            if not in_list:
                in_list = True
                html_output_list.append("<ul>")
            html_output_list.append(f'\t<li>{clean_text}</li>')
            continue
        elif in_list:
            html_output_list.append("</ul>")
            in_list = False

        if is_quote_item:
            if not in_blockquote:
                in_blockquote = True
                html_output_list.append('<blockquote>')
            html_output_list.append(clean_text)
            continue
        elif in_blockquote:
            html_output_list.append('</blockquote>')
            in_blockquote = False

        if clean_text == "" and processed_content == "":
            html_output_list.append("<br>")
            continue

        if is_header:
            html_output_list.append(f'<h{header_level}>{clean_text}</h{header_level}>')
            continue

        if is_hr:
            html_output_list.append("<hr>")
            continue

        html_output_list.append(f'<p>{clean_text}</p>')

    if in_list: html_output_list.append('</ul>')
    if in_blockquote: html_output_list.append('</blockquote>')
    if in_codeblock: html_output_list.append('</pre>')

    return "\n".join(html_output_list)


