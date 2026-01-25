from html.parser import HTMLParser
from HtmlNodes import HtmlNode, HtmlTextNode

class HtmlToTree(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack: list[HtmlNode] = []
        self.root_elems: list[HtmlNode] = []

    def generate_tree(self, html):
        self.feed(html)

    def get_tree(self):
        return self.root_elems

    def current_elem(self):
        size = len(self.stack)
        if size < 1:
            return None
        else:
            return self.stack[size-1]

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag)

        for attr in attrs:
            node.attributes.append(attr)

        current_elem = self.current_elem()
        if current_elem:
            current_elem.children.append(node)
        else:
            self.root_elems.append(node)

        self.stack.append(node)

    def handle_endtag(self, tag):
        if self.current_elem().tag_name != tag:
            print("HTML Parse Error!")
            exit(-1)
        
        self.stack.pop()

    def handle_data(self, data):
        if not data.isspace():
            print(f'Data is {data}')
            textNode = HtmlTextNode(data.strip())
            self.current_elem().children.append(textNode)
