"""Structural checks for this static site; not a full HTML/CSS standards validator."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import sys

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.refs = []
        self.anchors = []
        self.errors = []
        self.doctype = False
        self.lang = False
        self.title = False

    def handle_decl(self, decl):
        self.doctype |= decl.lower() == 'doctype html'

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = bool(a.get('lang'))
        if tag == 'title':
            self.title = True
        if 'id' in a:
            if a['id'] in self.ids:
                self.errors.append(f"duplicate id: {a['id']}")
            self.ids.add(a['id'])
        if tag == 'img' and 'alt' not in a:
            self.errors.append('img has no alt attribute')
        if a.get('href', '').startswith('#') and len(a['href']) > 1:
            self.anchors.append(unquote(a['href'][1:]))
        if tag in {'script', 'img', 'source'} and a.get('src'):
            self.refs.append(a['src'])
        if tag == 'link' and a.get('rel') == 'stylesheet' and a.get('href'):
            self.refs.append(a['href'])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f'closing void element: {tag}')
        elif not self.stack or self.stack[-1] != tag:
            self.errors.append(f'unexpected closing tag: {tag}')
        else:
            self.stack.pop()


def local_file(root, base, value):
    u = urlsplit(value)
    if u.scheme or u.netloc or not u.path:
        return None
    file = (base / unquote(u.path)).resolve()
    if not file.is_relative_to(root):
        raise ValueError(f'path outside project: {value}')
    return file


def validate(root):
    root = Path(root).resolve()
    errors = []
    for name in ['index.html', 'style.css', 'main.js']:
        if not (root / name).is_file():
            errors.append(f'missing required file: {name}')
    if errors:
        return errors
    parser = SiteParser()
    parser.feed((root / 'index.html').read_text(encoding='utf-8'))
    parser.close()
    errors.extend(parser.errors)
    if parser.stack:
        errors.append('unclosed HTML tags: ' + ', '.join(parser.stack))
    if not parser.doctype or not parser.lang or not parser.title:
        errors.append('HTML requires doctype, lang and title')
    for anchor in parser.anchors:
        if anchor not in parser.ids:
            errors.append(f'unknown anchor: #{anchor}')
    css_files = set()
    for ref in parser.refs:
        try:
            f = local_file(root, root, ref)
        except ValueError as e:
            errors.append(str(e))
            continue
        if f is not None:
            if not f.is_file():
                errors.append(f'missing local resource: {ref}')
            elif f.suffix.lower() == '.css':
                css_files.add(f)
    for f in css_files:
        css = f.read_text(encoding='utf-8')
        plain = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        plain = re.sub(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' ''', '', plain, flags=re.X)
        depth = 0
        for c in plain:
            depth += (c == '{') - (c == '}')
            if depth < 0:
                break
        if depth != 0:
            errors.append(f'unbalanced CSS braces: {f.name}')
        for value in re.findall(r'url\(\s*[\'"]?([^\'"\)]+)', css):
            try:
                resource = local_file(root, f.parent, value.strip())
                if resource is not None and not resource.is_file():
                    errors.append(f'missing CSS resource: {value}')
            except ValueError as e:
                errors.append(str(e))
    return errors


if __name__ == '__main__':
    errors = validate(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    for error in errors:
        print('ERROR:', error)
    if errors:
        sys.exit(1)
    print('PASS: HTML structure, identifiers, anchors, alt attributes and static local resources')
    print('PASS: CSS brace balance (not full standards validation)')
