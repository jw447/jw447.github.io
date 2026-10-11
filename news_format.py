"""Render bounded inline news formatting without accepting arbitrary HTML."""
from html import escape
from html.parser import HTMLParser


class NewsParser(HTMLParser):
    tags = {'b': 'strong', 'strong': 'strong', 'i': 'em', 'em': 'em', 'u': 'u', 's': 's'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.stack = []

    def handle_data(self, data):
        self.output.append(escape(data))

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.output.append('<br>')
        elif tag in self.tags:
            self.output.append('<' + self.tags[tag] + '>')
            self.stack.append(tag)
        else:
            self.output.append(escape(self.get_starttag_text()))

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack:
                current = self.stack.pop()
                self.output.append('</' + self.tags[current] + '>')
                if current == tag:
                    break
        elif tag not in self.tags:
            self.output.append(escape('</' + tag + '>'))


def render_news_text(value):
    parser = NewsParser()
    parser.feed(value)
    parser.close()
    while parser.stack:
        parser.output.append('</' + parser.tags[parser.stack.pop()] + '>')
    return ''.join(parser.output)
