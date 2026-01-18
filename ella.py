from html.parser import HTMLParser
from os import path
import json

class TickerCounter:
    def __init__(self, start=0, increment = 1):
        self.current_num = start
        self.increment = increment
    
    def get_current_num(self):
        return self.current_num

    def increment_ticker(self):
        self.current_num = self.current_num + self.increment

class HtmlNode:
    def __init__(self, tag_name, attributes=None, text=""):
        self.tag_name: str = tag_name
        if attributes is None:
           self.attributes = []
        else: 
            self.attributes: list[tuple[str, str]] = attributes
        self.text: str = text
        self.children: list["HtmlNode"] = []
    
    def __str__(self):
        return f'{self.tag_name}'

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack: list[HtmlNode] = []
        self.root_elems: list[HtmlNode] = []

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
            self.current_elem().text = data

def make_js(root_nodes):
    out_strings = []
    func_index = 0
    for root_node in root_nodes:
        ticker = TickerCounter(start=0, increment=1)
        strings = [
            f"function f{func_index}(){{",
            "const m = new Map();",
            "const e=[];"
        ]
        elems = process_node(root_node, ticker)
        for elem in elems:
            strings.append(elem)
        strings.extend([
            "return {rootElem:e[0],refs:m}}",
            "export{f0}"
            "\n"
        ])
        out_strings.append(strings)
    
    return out_strings

def process_node(html_node, ticker, parent_index=None):
    lines = []
    print(html_node)
    lines.append(f'e.push(document.createElement("{html_node.tag_name}"));')
    elem_index = ticker.get_current_num()
    if parent_index is None:
        root_index = 0
    else:
        lines.append(f'e[{parent_index}].appendChild(e[{elem_index}]);')
        root_index = parent_index +1
    
    if html_node.text:
        lines.append(f'e[{elem_index}].innerText="{html_node.text}";')

    for attribute in html_node.attributes:
        if attribute[0] == "data-name" and attribute[1][0:3] == "id-":
            name = attribute[1][3:]
            lines.append(f'm.set("{name}",e[{elem_index}]);')
            #lines.append(f'e[{elem_index}].setAttribute("{attribute[0]}","{name}");')
        else:
            lines.append(f'e[{elem_index}].setAttribute("{attribute[0]}","{attribute[1]}");')

    for child in html_node.children:
        ticker.increment_ticker()
        res_nodes = process_node(child, ticker, root_index)
        lines.extend(res_nodes)
    
    return lines

def tree_from_html(html):
    parser = MyHTMLParser()
    parser.feed(html)
    tree = parser.get_tree()
    return tree

def process(file_path, output_dir):
    file = path.split(file_path)[1]
    name = file.split(".")[0]

    with open(file_path, 'r') as file:
        html = file.read(-1)
    tree = tree_from_html(html)

    res = make_js(tree)
    output = ''.join(res[0])

    outpath = path.join(output_dir, f'{name}.js')
    with open(outpath, 'w') as file:
        file.write(output)

def process_multiple(files, output_dir):
    for file in files:
        process(file, output_dir)

def main():
    conf_path = "./build.json"
    with open(conf_path,'r') as f:
        conf = json.load(f)
    process_multiple(conf["source_files"], conf["out_dir"])

if __name__ == '__main__':
    main()