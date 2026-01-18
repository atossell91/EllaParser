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

class JsBuilder:
    def __init__(self, name):
        self.root = None
        self.statements = []
        self.index_counter = TickerCounter(0, 1)
        self.component_name = name
        self.elems_arr_name = 'e'
        self.id_tag_name = 'data-name'
        self.id_tag_prefix = "id-"
        self.map_name = "map"
        self.initial_statements = [
            f'function {self.component_name}(){{',
            f'const {self.elems_arr_name}=[];',
            f'const {self.map_name}=new Map();'
        ]
        self.final_statements = [
            f'return{{elems:{self.elems_arr_name}[0],refs:{self.map_name}}}}}',
            f'export{{{self.component_name}}}'
        ]
        self.pretty_indent = "    "

    def is_id_attribute(self, name, value):
        return name == self.id_tag_name and value[0:len(self.id_tag_prefix)] == self.id_tag_prefix

    def apply_attributes(self, elem_index, attributes):
        for attribute in attributes:
            name = attribute[0]
            value = attribute[1]

            if self.is_id_attribute(name, value):
                key = value[len(self.id_tag_prefix):]
                statement = f'{self.map_name}.set("{key}",{self.elems_arr_name}[{elem_index}]);'
                self.statements.append(statement)
            else:
                statement = f'{self.elems_arr_name}[{elem_index}].setAttribute("{name}","{value}");'
                self.statements.append(statement)
    
    def apply_data(self, elem_index, data):
        statement = f'{self.elems_arr_name}[{elem_index}].innerText="{data}";'
        self.statements.append(statement)

    def create_element(self, tag):
        self.statements.append(f'{self.elems_arr_name}.push(document.createElement("{tag}"));')
        self.index_counter.increment_ticker()

    def append_element(self, parent_index, child_index):
        parent = f'{self.elems_arr_name}[{parent_index}]'
        child = f'{self.elems_arr_name}[{child_index}]'
        statement = f'{parent}.appendChild({child});'
        self.statements.append(statement)

    def start_walk(self, tree):
        self.create_element(tree.tag_name)
        current_index = self.index_counter.get_current_num()-1
        self.apply_attributes(current_index, tree.attributes)
        if len(tree.text) > 0:
            self.apply_data(current_index, tree.text)
        for child in tree.children:
            self.walk(child, current_index)

    def walk(self, tree, parent_index):
        current_index = self.index_counter.get_current_num() #must come before create_element!!
        self.create_element(tree.tag_name)
        self.apply_attributes(current_index, tree.attributes)
        if len(tree.text) > 0:
            self.apply_data(current_index, tree.text)
        self.append_element(parent_index, current_index)

        for child in tree.children:
            self.walk(child, current_index)

    def get_pretty_str(self):
        output = ''
        for statement in self.initial_statements:
            output = output + statement + '\n'

        for statement in self.statements:
            output = output + self.pretty_indent + statement + '\n'

        for statement in self.final_statements:
            output = output + statement + '\n'
        
        return output

    def get_ugly_str(self):
        output = ''
        for statement in self.initial_statements:
            output = output + statement

        for statement in self.statements:
            output = output + statement

        for statement in self.final_statements:
            output = output + statement
        
        return output

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

    builder = JsBuilder(name)
    builder.start_walk(tree[0])
    output = builder.get_ugly_str()

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